from typing import Any

from samtranslator.metrics.method_decorator import cw_timer
from samtranslator.model.exceptions import InvalidResourceAttributeTypeException
from samtranslator.plugins.globals.globals import Globals, InvalidGlobalsSectionException
from samtranslator.public.exceptions import InvalidDocumentException
from samtranslator.public.plugins import BasePlugin
from samtranslator.public.sdk.template import SamTemplate

_API_RESOURCE = "AWS::Serverless::Api"


class GlobalsPlugin(BasePlugin):
    """
    Plugin to process Globals section of a SAM template before the template is translated to CloudFormation.
    """

    @cw_timer(prefix="Plugin-Globals")
    def on_before_transform_template(self, template_dict: dict[str, Any]) -> None:
        """
        Hook method that runs before a template gets transformed. In this method, we parse and process Globals section
        from the template (if present).

        :param dict template_dict: SAM template as a dictionary
        """
        pass
