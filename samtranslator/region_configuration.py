import boto3

from .translator.arn_generator import ArnGenerator, NoRegionFound


class RegionConfiguration:
    """
    There are times when certain services, or certain configurations of a service are not supported in a region. This
    class abstracts all region/partition specific configuration.
    """

    @classmethod
    def is_apigw_edge_configuration_supported(cls) -> bool:
        """
        # API Gateway defaults to EDGE endpoint configuration in all regions in AWS partition. But for other partitions,
        # such as GovCloud, they don't support Edge.

        :return: True, if API Gateway does not support Edge configuration
        """
        partition = ArnGenerator.get_partition_name()
        return not (partition.startswith("aws-iso") or partition in ["aws-us-gov", "aws-cn", "aws-eusc"])

    @classmethod
    def is_service_supported(cls, service, region=None):  # type: ignore[no-untyped-def]
        """
        Not all services are supported in all regions.  This method returns whether a given
        service is supported in a given region.  If no region is specified, the current region
        (as identified by boto3) is used.
        https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/

        :param service: service code (string used to obtain a boto3 client for the service)
        :param region: region identifier (e.g., us-east-1)
        :return: True, if the service is supported in the region
        """
        pass
