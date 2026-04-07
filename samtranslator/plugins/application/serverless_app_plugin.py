import copy
import json
import logging
import re
from collections.abc import Callable
from time import sleep
from typing import Any

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError

from samtranslator.intrinsics.actions import FindInMapAction
from samtranslator.intrinsics.resolver import IntrinsicsResolver
from samtranslator.metrics.method_decorator import cw_timer
from samtranslator.model.exceptions import InvalidResourceException
from samtranslator.plugins import BasePlugin
from samtranslator.plugins.exceptions import InvalidPluginException
from samtranslator.public.sdk.resource import SamResourceType
from samtranslator.public.sdk.template import SamTemplate
from samtranslator.region_configuration import RegionConfiguration
from samtranslator.utils.constants import BOTO3_CONNECT_TIMEOUT
from samtranslator.validator.value_validator import sam_expect

LOG = logging.getLogger(__name__)

PLUGIN_METRICS_PREFIX = "Plugin-ServerlessApp"


class ServerlessAppPlugin(BasePlugin):
    """
    Resolves all the ApplicationId and Semantic Version pairs
    for AWS::Serverless::Application to template URLs.

    To retrieve a template from the Serverless Application Repository (SAR),
    this plugin needs to call the CreateCloudFormationTemplate API, which
    initiates the process of creating and copying the application template and
    all of its assets from the region it is in to the current region. This
    API returns a pre-signed S3 url that can be passed to CFN. When the template
    reaches ACTIVE status, all assets have been successfully copied and are
    ready to be deployed. This plugin verfies that applications are in an
    ACTIVE state by calling the GetCloudFormation API from SAR.
    """

    SUPPORTED_RESOURCE_TYPE = "AWS::Serverless::Application"
    SLEEP_TIME_SECONDS = 2
    # CloudFormation times out on transforms after 2 minutes, so setting this
    # timeout below that to leave some buffer
    TEMPLATE_WAIT_TIMEOUT_SECONDS = 105
    APPLICATION_ID_KEY = "ApplicationId"
    SEMANTIC_VERSION_KEY = "SemanticVersion"
    LOCATION_KEY = "Location"
    TEMPLATE_URL_KEY = "TemplateUrl"

    def __init__(
        self,
        sar_client: BaseClient | None = None,
        wait_for_template_active_status: bool = False,
        validate_only: bool = False,
        parameters: dict[str, Any] | None = None,
        sar_client_creator: Callable[[], BaseClient] | None = None,
    ) -> None:
        """
        Initialize the plugin.

        Explain that Validate_only uses a different API call, and does not produce a valid template.
        :param boto3.client sar_client: The boto3 client to use to access the Serverless Application Repository
        :param bool wait_for_template_active_status: Flag to wait for all templates to become active
        :param bool validate_only: Flag to only validate application access (uses get_application API instead)
        :param bool sar_client_creator: A function to return a SAR client.
                                        Only used when sar_client is None and SAR calls are made.
        """
        super().__init__()
        if parameters is None:
            parameters = {}
        self._applications: dict[tuple[str, str], Any] = {}
        self._in_progress_templates: list[tuple[str, str]] = []
        self.__sar_client = sar_client
        self._sar_client_creator = sar_client_creator
        self._wait_for_template_active_status = wait_for_template_active_status
        self._validate_only = validate_only
        self._parameters = parameters
        self._total_wait_time = 0

        # make sure the flag combination makes sense
        if self._validate_only is True and self._wait_for_template_active_status is True:
            message = "Cannot set both validate_only and wait_for_template_active_status flags to True."
            raise InvalidPluginException(ServerlessAppPlugin.__name__, message)

    @property
    def _sar_client(self) -> BaseClient:
        # Lazy initialization of the client-create it when it is needed
        pass

    @staticmethod
    def _make_app_key(app_id: Any, semver: Any) -> tuple[str, str]:
        """Generate a key that is always hashable."""
        pass

    @cw_timer(prefix=PLUGIN_METRICS_PREFIX)
    def on_before_transform_template(self, template_dict):  # type: ignore[no-untyped-def]
        """
        Hook method that gets called before the SAM template is processed.
        The template has passed the validation and is guaranteed to contain a non-empty "Resources" section.

        This plugin needs to run as soon as possible to allow some time for templates to become available.
        This verifies that the user has access to all specified applications.

        :param dict template_dict: Dictionary of the SAM template
        """
        pass

    def _make_service_call_with_retry(self, service_call, app_id, semver, key, logical_id):  # type: ignore[no-untyped-def]
        pass

    def _replace_value(self, input_dict, key, intrinsic_resolvers):  # type: ignore[no-untyped-def]
        pass

    def _get_intrinsic_resolvers(self, mappings):  # type: ignore[no-untyped-def]
        pass

    def _resolve_location_value(self, value, intrinsic_resolvers):  # type: ignore[no-untyped-def]
        pass

    def _can_process_application(self, app):  # type: ignore[no-untyped-def]
        """
        Determines whether or not the on_before_transform_template event can process this application

        :param dict app: the application and its properties
        """
        pass

    def _handle_get_application_request(self, app_id, semver, key, logical_id):  # type: ignore[no-untyped-def]
        """
        Method that handles the get_application API call to the serverless application repo

        This method puts something in the `_applications` dictionary because the plugin expects
        something there in a later event.

        :param string app_id: ApplicationId
        :param string semver: SemanticVersion
        :param string key: The dictionary key consisting of (ApplicationId, SemanticVersion)
        :param string logical_id: the logical_id of this application resource
        """
        pass

    def _handle_create_cfn_template_request(self, app_id, semver, key, logical_id):  # type: ignore[no-untyped-def]
        """
        Method that handles the create_cloud_formation_template API call to the serverless application repo

        :param string app_id: ApplicationId
        :param string semver: SemanticVersion
        :param string key: The dictionary key consisting of (ApplicationId, SemanticVersion)
        :param string logical_id: the logical_id of this application resource
        """
        pass

    def _sanitize_sar_str_param(self, param):  # type: ignore[no-untyped-def]
        """
        Sanitize SAR API parameter expected to be a string.

        If customer passes something like 1.0 as SemanticVersion, python
        converts it to a float instead of a basestring, so need to explicitly
        convert it for API calls to SAR that expect a string input.

        :param object param: Parameter to sanitize
        """
        pass

    @cw_timer(prefix=PLUGIN_METRICS_PREFIX)
    def on_before_transform_resource(self, logical_id, resource_type, resource_properties):  # type: ignore[no-untyped-def]
        """
        Hook method that gets called before "each" SAM resource gets processed

        Replaces the ApplicationId and Semantic Version pairs with a TemplateUrl.

        :param string logical_id: Logical ID of the resource being processed
        :param string resource_type: Type of the resource being processed
        :param dict resource_properties: Properties of the resource
        """
        pass

    def _check_for_dictionary_key(self, logical_id, dictionary, keys):  # type: ignore[no-untyped-def]
        """
        Checks a dictionary to make sure it has a specific key. If it does not, an
        InvalidResourceException is thrown.

        :param string logical_id: logical id of this resource
        :param dict dictionary: the dictionary to check
        :param list keys: list of keys that should exist in the dictionary
        """
        pass

    @cw_timer(prefix=PLUGIN_METRICS_PREFIX)
    def on_after_transform_template(self, template):  # type: ignore[no-untyped-def]
        """
        Hook method that gets called after the template is processed

        Go through all the stored applications and make sure they're all ACTIVE.

        :param dict template: Dictionary of the SAM template
        """
        pass

    def _get_sleep_time_sec(self) -> int:
        pass

    def _is_template_active(self, response: dict[str, Any], application_id: str, template_id: str) -> bool:
        """
        Checks the response from a SAR service call; returns True if the template is active,
        throws an exception if the request expired and returns False in all other cases.

        :param dict response: the response dictionary from the app repo
        :param string application_id: the ApplicationId
        :param string template_id: the unique TemplateId for this application
        """
        pass

    @cw_timer(prefix="External", name="SAR")
    def _sar_service_call(self, service_call_lambda, logical_id, *args):  # type: ignore[no-untyped-def]
        """
        Handles service calls and exception management for service calls
        to the Serverless Application Repository.

        :param lambda service_call_lambda: lambda function that contains the service call
        :param string logical_id: Logical ID of the resource being processed
        :param list *args: arguments for the service call lambda
        """
        pass

    def _resource_is_supported(self, resource_type):  # type: ignore[no-untyped-def]
        """
        Is this resource supported by this plugin?

        :param string resource_type: Type of the resource
        :return: True, if this plugin supports this resource. False otherwise
        """
        pass

    def _get_application(self, app_id, semver):  # type: ignore[no-untyped-def]
        pass

    def _create_cfn_template(self, app_id, semver):  # type: ignore[no-untyped-def]
        pass

    def _get_cfn_template(self, app_id, template_id):  # type: ignore[no-untyped-def]
        pass
