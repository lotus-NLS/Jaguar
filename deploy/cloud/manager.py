from __future__ import annotations

from deploy.cloud.components import AWSRegions
from deploy.cloud.components import EC2Manger, LambdaManager, DatabaseManager, IAM_Manager

# ----------------------------------------------

class CloudManager:
    def __init__(self, region: AWSRegions) -> None:
        self.region: str = region.value

        # Set managers
        self.ec2 : EC2Manger = EC2Manger(region=region)
        self.lambda_aws : LambdaManager = LambdaManager(region=region)
        self.iam : IAM_Manager = IAM_Manager(region=region)
        self.database : DatabaseManager = DatabaseManager(region=region)

        # self.elb_client = boto3.client('elbv2', region_name=self.region)
        # self.events_client = boto3.client('events', region_name=self.region)