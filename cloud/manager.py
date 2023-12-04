from __future__ import annotations

from entities import AWSRegions
from services import EC2AWS, LambdaAWS, DatabaseAWS, IAMAWS

# ----------------------------------------------

class CloudManager:
    def __init__(self, region: AWSRegions) -> None:
        self.region: str = region.value

        # Set managers
        self.ec2 : EC2AWS = EC2AWS(region=region)
        self.lambda_aws : LambdaAWS = LambdaAWS(region=region)
        self.iam : IAMAWS = IAMAWS(region=region)
        self.database : DatabaseAWS = DatabaseAWS(region=region)

        # self.elb_client = boto3.client('elbv2', region_name=self.region)
        # self.events_client = boto3.client('events', region_name=self.region)