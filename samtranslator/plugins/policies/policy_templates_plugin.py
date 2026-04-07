from samtranslator.metrics.method_decorator import cw_timer
from samtranslator.model.exceptions import InvalidResourceException
from samtranslator.model.intrinsics import is_intrinsic_if, is_intrinsic_no_value
from samtranslator.model.resource_policies import PolicyTypes, ResourcePolicies
from samtranslator.plugins import BasePlugin
from samtranslator.policy_template_processor.exceptions import InsufficientParameterValues, InvalidParameterValues
from samtranslator.policy_template_processor.processor import PolicyTemplatesProcessor


class PolicyTemplatesForResourcePlugin(BasePlugin):
    """
    Use this plugin to allow the usage of Policy Templates in `Policies` section of AWS::Serverless::Function or
    AWS::Serverless::StateMachine resource.
    This plugin runs a `before_transform_resource` hook and converts policy templates into regular policy statements
    for the core SAM translator to take care of.
    """

    _plugin_name = ""
    SUPPORTED_RESOURCE_TYPE = {"AWS::Serverless::Function", "AWS::Serverless::StateMachine"}

    def __init__(self, policy_template_processor: PolicyTemplatesProcessor) -> None:
        """
        Initialize the plugin.

        :param policy_template_processor: Instance of the PolicyTemplateProcessor that knows how to convert policy
            template to a statement
        """
        super().__init__()

        self._policy_template_processor = policy_template_processor

    @cw_timer(prefix="Plugin-PolicyTemplates")
    def on_before_transform_resource(self, logical_id, resource_type, resource_properties):  # type: ignore[no-untyped-def]
        """
        Hook method that gets called before "each" SAM resource gets processed

        :param string logical_id: Logical ID of the resource being processed
        :param string resource_type: Type of the resource being processed
        :param dict resource_properties: Properties of the resource
        """
        pass

    def _process_intrinsic_if_policy_template(self, logical_id, policy_entry):  # type: ignore[no-untyped-def]
        pass

    def _process_policy_template(self, logical_id, template_data):  # type: ignore[no-untyped-def]
        # We are processing policy templates. We know they have a particular structure:
        # {"templateName": { parameter_values_dict }}
        pass

    def _is_supported(self, resource_type):  # type: ignore[no-untyped-def]
        """
        Is this resource supported by this plugin?

        :param string resource_type: Type of the resource
        :return: True, if this plugin supports this resource. False otherwise
        """
        pass
