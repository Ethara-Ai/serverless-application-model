import copy
from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar, Union

from samtranslator.metrics.method_decorator import cw_timer
from samtranslator.model.eventsources.push import Api
from samtranslator.model.intrinsics import MIN_NUM_CONDITIONS_TO_COMBINE, make_combined_condition
from samtranslator.open_api.open_api import OpenApiEditor
from samtranslator.public.exceptions import InvalidDocumentException, InvalidEventException, InvalidResourceException
from samtranslator.public.plugins import BasePlugin
from samtranslator.public.sdk.resource import SamResource, SamResourceType
from samtranslator.public.sdk.template import SamTemplate
from samtranslator.swagger.swagger import SwaggerEditor
from samtranslator.utils.py27hash_fix import Py27Dict
from samtranslator.validator.value_validator import sam_expect

T = TypeVar("T", bound=Union[type[OpenApiEditor], type[SwaggerEditor]])


class ImplicitApiPlugin(BasePlugin, Generic[T], metaclass=ABCMeta):
    """
    This plugin provides Implicit API shorthand syntax in the SAM Spec.
    https://github.com/aws/serverless-application-model/blob/master/versions/2016-10-31.md#api

    Implicit API syntax is just a syntactic sugar, which will be translated to AWS::Serverless::Api resource.
    This is the only event source implemented as a plugin. Other event sources are not plugins because,
    DynamoDB event source, for example, is not creating the DynamoDB resource. It just adds
    a connection between the resource and Lambda. But with Implicit APIs, it creates and configures the API
    resource in addition to adding the connection. This plugin will simply tackle the resource creation
    bits and delegate the connection work to core translator.

    To sum up, here is the split of responsibilities:

    * This Plugin: Creates AWS::Serverless::Api and generates a Swagger with Methods, Paths, CORS, API Keys,
                   Usage Plans etc, essentially anything that configures API Gateway.

    * API Event Source (In Core Translator): ONLY adds the Lambda Integration ARN to appropriate method/path
                                             in Swagger. Does **not** configure the API by any means.

    """

    # Name of the event property name to referring api id in the event source.
    API_ID_EVENT_PROPERTY: str
    # The logical id of the implicit API resource
    IMPLICIT_API_LOGICAL_ID: str
    IMPLICIT_API_CONDITION: str
    API_EVENT_TYPE: str
    SERVERLESS_API_RESOURCE_TYPE: str
    EDITOR_CLASS: T

    def __init__(self) -> None:
        """
        Initialize the plugin.
        """
        super().__init__()

        self.existing_implicit_api_resource: SamResource | None = None
        # dict containing condition (or None) for each resource path+method for all APIs. dict format:
        # {api_id: {path: {method: condition_name_or_None}}}
        self.api_conditions: dict[str, Any] = {}
        self.api_deletion_policies: dict[str, Any] = {}
        self.api_update_replace_policies: dict[str, Any] = {}

    @abstractmethod
    def _process_api_events(
        self,
        function: SamResource,
        api_events: dict[str, dict[str, Any]],
        template: SamTemplate,
        condition: str | None = None,
        deletion_policy: str | None = None,
        update_replace_policy: str | None = None,
    ) -> None:
        """
        Actually process given API events. Iteratively adds the APIs to Swagger JSON in the respective Serverless::Api
        resource from the template

        :param SamResource function: SAM function containing the API events to be processed
        :param dict api_events: API Events extracted from the function. These events will be processed
        :param SamTemplate template: SAM Template where Serverless::Api resources can be found
        :param str condition: optional; this is the condition that is on the resource with the API event
        """

    @abstractmethod
    def _get_api_definition_from_editor(self, editor):  # type: ignore[no-untyped-def]
        """
        Required function that returns the api body from the respective editor
        """

    @abstractmethod
    def _generate_implicit_api_resource(self) -> dict[str, Any]:
        """
        Helper function implemented by child classes that create a new implicit API resource
        """

    def _add_tags_to_implicit_api_if_necessary(
        self, event_properties: dict[str, Any], resource: SamResource, template: SamTemplate
    ) -> None:
        """
        Decides whether to add tags to the implicit api resource.
        :param dict template_dict: SAM template dictionary
        """
        pass

    @cw_timer(prefix="Plugin-ImplicitApi")
    def on_before_transform_template(self, template_dict):  # type: ignore[no-untyped-def]
        """
        Hook method that gets called before the SAM template is processed.
        The template has pass the validation and is guaranteed to contain a non-empty "Resources" section.

        :param dict template_dict: Dictionary of the SAM template
        """
        pass

    def _add_implicit_api_id_if_necessary(self, event_properties):  # type: ignore[no-untyped-def]
        """
        Events for implicit APIs will *not* have the RestApiId property. Absence of this property means this event
        is associated with the Serverless::Api ImplicitAPI resource. This method solifies this assumption by adding
        RestApiId property to events that don't have them.

        :param dict event_properties: Dictionary of event properties
        """
        pass

    def _get_api_events(self, resource):  # type: ignore[no-untyped-def]
        """
        Method to return a dictionary of API Events on the resource

        :param SamResource resource: SAM Resource object
        :return dict: Dictionary of API events along with any other configuration passed to it.
            Example: {
                FooEvent: {Path: "/foo", Method: "post", RestApiId: blah, MethodSettings: {<something>},
                            Cors: {<something>}, Auth: {<something>}},
                BarEvent: {Path: "/bar", Method: "any", MethodSettings: {<something>}, Cors: {<something>},
                            Auth: {<something>}}"
            }
        """
        pass

    def _add_api_to_swagger(self, event_id, event_properties, template):  # type: ignore[no-untyped-def]
        """
        Adds the API path/method from the given event to the Swagger JSON of Serverless::Api resource this event
        refers to.

        :param string event_id: LogicalId of the event
        :param dict event_properties: Properties of the event
        :param SamTemplate template: SAM Template to search for Serverless::Api resources
        """
        pass

    def _get_api_id(self, event_properties: dict[str, Any]) -> Any:
        """
        Get API logical id from API event properties.

        Handles case where API id is not specified or is a reference to a logical id.
        """
        pass

    def _maybe_add_condition_to_implicit_api(self, template_dict):  # type: ignore[no-untyped-def]
        """
        Decides whether to add a condition to the implicit api resource.
        :param dict template_dict: SAM template dictionary
        """
        pass

    def _maybe_add_deletion_policy_to_implicit_api(self, template_dict):  # type: ignore[no-untyped-def]
        """
        Decides whether to add a deletion policy to the implicit api resource.
        :param dict template_dict: SAM template dictionary
        """
        pass

    def _maybe_add_update_replace_policy_to_implicit_api(self, template_dict):  # type: ignore[no-untyped-def]
        """
        Decides whether to add an update replace policy to the implicit api resource.
        :param dict template_dict: SAM template dictionary
        """
        pass

    def _add_combined_condition_to_template(self, template_dict, condition_name, conditions_to_combine):  # type: ignore[no-untyped-def]
        """
        Add top-level template condition that combines the given list of conditions.

        :param dict template_dict: SAM template dictionary
        :param string condition_name: Name of top-level template condition
        :param list conditions_to_combine: List of conditions that should be combined (via OR operator) to form
                                           top-level condition.
        """
        pass

    def _maybe_add_conditions_to_implicit_api_paths(self, template):  # type: ignore[no-untyped-def]
        """
        Add conditions to implicit API paths if necessary.

        Implicit API resource methods are constructed from API events on individual serverless functions within the SAM
        template. Since serverless functions can have conditions on them, it's possible to have a case where all methods
        under a resource path have conditions on them. If all of these conditions evaluate to false, the entire resource
        path should not be defined either. This method checks all resource paths' methods and if all methods under a
        given path contain a condition, a composite condition is added to the overall template Conditions section and
        that composite condition is added to the resource path.
        """
        pass

    def _path_condition_name(self, api_id, path):  # type: ignore[no-untyped-def]
        """
        Generate valid condition logical id from the given API logical id and swagger resource path.
        """
        pass

    def _maybe_remove_implicit_api(self, template):  # type: ignore[no-untyped-def]
        """
        Implicit API resource are tentatively added to the template for uniform handling of both Implicit & Explicit
        APIs. They need to removed from the template, if there are *no* API events attached to this resource.
        This method removes the Implicit API if it does not contain any Swagger paths (added in response to API events).

        :param SamTemplate template: SAM Template containing the Implicit API resource
        """
        pass

    def _validate_api_event(self, event_id: str, event_properties: dict[str, Any]) -> tuple[str, str, str]:
        """Validate and return api_id, path, method."""
        pass

    def _update_resource_attributes_from_api_event(
        self,
        api_id: str,
        path: str,
        method: str,
        condition: str | None,
        deletion_policy: str | None,
        update_replace_policy: str | None,
    ) -> None:
        pass
