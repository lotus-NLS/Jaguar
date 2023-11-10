from __future__ import annotations

from enum import Enum
from typing import Optional


class AWSRegions(Enum):
    US_EAST_1 = 'us-east-1'
    US_EAST_2 = 'us-east-2'
    US_WEST_1 = 'us-west-1'
    US_WEST_2 = 'us-west-2'
    EU_WEST_1 = 'eu-west-1'
    EU_WEST_2 = 'eu-west-2'
    EU_CENTRAL_1 = 'eu-central-1'
    EU_NORTH_1 = 'eu-north-1'
    AP_SOUTHEAST_1 = 'ap-southeast-1'
    AP_SOUTHEAST_2 = 'ap-southeast-2'
    AP_NORTHEAST_1 = 'ap-northeast-1'
    AP_NORTHEAST_2 = 'ap-northeast-2'
    AP_SOUTH_1 = 'ap-south-1'
    AP_EAST_1 = 'ap-east-1'
    CA_CENTRAL_1 = 'ca-central-1'
    SA_EAST_1 = 'sa-east-1'
    CN_NORTH_1 = 'cn-north-1'
    CN_NORTHWEST_1 = 'cn-northwest-1'
    AF_SOUTH_1 = 'af-south-1'
    ME_SOUTH_1 = 'me-south-1'


class EC2Type(Enum):
    T2_MICRO = 't2.micro'
    T2_SMALL = 't2.small'
    T3_MICRO = 't3.micro'
    T3_SMALL = 't3.small'


class ImageID(Enum):
    UBUNTU_2204 = 'ami-0fe8bec493a81c7da'


class InstanceState(Enum):
    RUNNING = 'instance_running'
    STOPPED = 'instance_stopped'
    # You can add more states as needed


class InstanceTemplate:
    def __init__(self, image_id: ImageID,
                 ec2_type: EC2Type,
                 setup_script: str = '',
                 key_pair_name: Optional[str] = None,
                 network_interface_id: Optional[str] = None,
                 instance_name: Optional[str] = None,
                 security_group: Optional[str] = None,
                 iam_instance_profile: Optional[str] = None) -> None:
        self.image_id: str = image_id.value
        self.ec2_type: str = ec2_type.value
        self.setup_script: Optional[str] = setup_script
        self.key_pair_name: Optional[str] = key_pair_name
        self.network_interface_id: Optional[str] = network_interface_id
        self.instance_name: Optional[str] = instance_name
        self.security_group: Optional[str] = security_group
        self.iam_instance_profile: Optional[str] = iam_instance_profile

    @classmethod
    def make_default(cls) -> InstanceTemplate:
        new_instance = cls(image_id=ImageID.UBUNTU_2204, ec2_type=EC2Type.T3_MICRO)
        return new_instance


class ServiceURL(Enum):
    LAMBDA = 'lambda.amazonaws.com'
    EC2 = 'ec2.amazonaws.com'