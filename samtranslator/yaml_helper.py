import yaml
from yaml import ScalarNode, SequenceNode

# This helper copied almost entirely from
# https://github.com/aws/aws-cli/blob/develop/awscli/customizations/cloudformation/yamlhelper.py


def yaml_parse(yamlstr):  # type: ignore[no-untyped-def]
    """Parse a yaml string"""
    yaml.SafeLoader.add_multi_constructor("!", intrinsics_multi_constructor)  # type: ignore[no-untyped-call]
    return yaml.safe_load(yamlstr)


def intrinsics_multi_constructor(loader, tag_prefix, node):  # type: ignore[no-untyped-def]
    """
    YAML constructor to parse CloudFormation intrinsics.
    This will return a dictionary with key being the instrinsic name
    """
    pass
