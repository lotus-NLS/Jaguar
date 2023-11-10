import boto3
import json
from typing import Optional
from .enums import AWSRegions, ServiceURL

# ----------------------------------------------

class IAM_Manager:
    def __init__(self, region : AWSRegions):
        self.region : str = region.value
        self.client = boto3.client('iam', region_name=self.region)


    def create_iam(self, role_name: str, policy_arns: list[str], service : ServiceURL):
        try:
            trust_relationship = self.get_trust_relationship(service)
            if trust_relationship is None:
                raise ValueError(f'Could not find trust relationship for service {service}')

            self.client.create_role(RoleName=role_name,AssumeRolePolicyDocument=json.dumps(trust_relationship))
            for policy_arn in policy_arns:
                self.client.attach_role_policy(RoleName=role_name,PolicyArn=policy_arn)
            print(f"IAM Role created: {role_name}")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None


    # ----------------------------------------------
    # get

    @staticmethod
    def get_trust_relationship(service : ServiceURL) -> Optional[dict]:
        statement_header = {
            "Effect": "Allow",
            "Principal": {"Service": service.value},
            "Action": "sts:AssumeRole"
        }

        trust_relationship = {
            "Version": "2012-10-17",
            "Statement": [statement_header]
        }

        return trust_relationship


    def get_iam_roles(self) -> list[dict]:
        try:
            response = self.client.list_roles()
            roles = response.get('Roles', [])

            print(f'Found the following roles')
            for role in roles:
                print(f"Role Name: {role['RoleName']}, ARN: {role['Arn']}, Creation Date: {role['CreateDate']}")

            return roles

        except Exception as e:
            print(f"An error occurred: {e}")
            return []

