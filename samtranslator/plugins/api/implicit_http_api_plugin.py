from typing import Any, cast

from samtranslator.model.intrinsics import make_conditional
from samtranslator.plugins.api.implicit_api_plugin import ImplicitApiPlugin
from samtranslator.public.open_api import OpenApiEditor
from samtranslator.public.sdk.resource import SamResource, SamResourceType
from samtranslator.sdk.template import SamTemplate
from samtranslator.validator.value_validator import sam_expect


class ImplicitHttpApiPlugin(ImplicitApiPlugin[type[OpenApiEditor]]):
    """
    This plugin provides Implicit Http API shorthand syntax in the SAM Spec.

    Implicit API syntax is just a syntactic sugar, which will be translated to AWS::Serverless::HttpApi resource.
    This is the only event source implemented as a plugin. Other event sources are not plugins because,
    DynamoDB event source, for example, is not creating the DynamoDB resource. It just adds
    a connection between the resource and Lambda. But with Implicit APIs, it creates and configures the API
    resource in addition to adding the connection. This plugin will simply tackle the resource creation bits
    and delegate the connection work to core translator.

    To sum up, here is the split of responsibilities:
    * This Plugin: Creates AWS::Serverless::HttpApi and generates OpenApi with Methods, Paths, Auth, etc,
                                            essentially anything that configures API Gateway.
    * API Event Source (In Core Translator): ONLY adds the Lambda Integration ARN to appropriate method/path
                                             in OpenApi. Does **not** configure the API by any means.
    """

    API_ID_EVENT_PROPERTY = "ApiId"
    IMPLICIT_API_LOGICAL_ID = "ServerlessHttpApi"
    IMPLICIT_API_CONDITION = "ServerlessHttpApiCondition"
    API_EVENT_TYPE = "HttpApi"
    SERVERLESS_API_RESOURCE_TYPE = SamResourceType.HttpApi.value
    EDITOR_CLASS = OpenApiEditor

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
        Actually process given HTTP API events. Iteratively adds the APIs to OpenApi JSON in the respective
        AWS::Serverless::HttpApi resource from the template

        :param SamResource function: SAM Function containing the API events to be processed
        :param dict api_events: Http API Events extracted from the function. These events will be processed
        :param SamTemplate template: SAM Template where AWS::Serverless::HttpApi resources can be found
        :param str condition: optional; this is the condition that is on the function with the API event
        """
        pass

    def _generate_implicit_api_resource(self) -> dict[str, Any]:
        """
        Uses the implicit API in this file to generate an Implicit API resource
        """
        pass

    def _get_api_definition_from_editor(self, editor: OpenApiEditor) -> dict[str, Any]:
        """
        Helper function to return the OAS definition from the editor
        """
        pass

    def _add_route_settings_to_api(
        self, event_id: str, event_properties: dict[str, Any], template: SamTemplate, condition: str | None
    ) -> None:
        """
        Adds the RouteSettings for this path/method from the given event to the RouteSettings configuration
        on the AWS::Serverless::HttpApi that this refers to.

        :param string event_id: LogicalId of the event
        :param dict event_properties: Properties of the event
        :param SamTemplate template: SAM Template to search for Serverless::HttpApi resources
        :param string condition: Condition on this HttpApi event (if any)
        """
        pass


class ImplicitHttpApiResource(SamResource):
    """
    Returns a AWS::Serverless::HttpApi resource representing the Implicit APIs. The returned resource
    includes the empty OpenApi along with default values for other properties.
    """

    def __init__(self) -> None:
        open_api = OpenApiEditor.gen_skeleton()

        resource = {
            "Type": SamResourceType.HttpApi.value,
            "Properties": {
                "DefinitionBody": open_api,
                # Internal property that means Event source code can add Events. Used only for implicit APIs, to
                # prevent back compatibility issues for explicit APIs
                "__MANAGE_SWAGGER": True,
            },
        }

        super().__init__(resource)
