from __future__ import annotations
from enum import Enum

# ---------------------------------------------------------
# General

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



# ---------------------------------------------------------
# EC2

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


# ---------------------------------------------------------
# Roles

class Service(Enum):
    LAMBDA = 'lambda.amazonaws.com'
    EC2 = 'ec2.amazonaws.com'


class Policy(Enum):
    LAMBDA_BASIC_EXECUTION_ROLE = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    SECRETS_MANAGER_READ_WRITE = 'arn:aws:iam::aws:policy/SecretsManagerReadWrite'
    S3_FULL_ACCESS = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
