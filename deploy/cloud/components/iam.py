import boto3
from .enums import AWSRegions
import json

# ----------------------------------------------

class IAM_Manager:
    def __init__(self, region : AWSRegions):
        self.region : str = region.value
        self.iam_client = boto3.client('iam',region_name=self.region)


    @staticmethod
    def create_lambda_iam(role_name: str, policy_arns: list[str]):
        try:
            trust_relationship = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }

            # Create the role
            iam_client = boto3.client('iam')
            role = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_relationship)
            )

            # Attach policies to the role
            for policy_arn in policy_arns:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )

            print(f"IAM Role created: {role_name}")
            return role['Role']['Arn']

        except Exception as e:
            print(f"An error occurred: {e}")
            return None


    def get_iam_roles(self) -> list[dict]:
        try:
            response = self.iam_client.list_roles()
            roles = response.get('Roles', [])

            print(f'Found the following roles')
            for role in roles:
                print(f"Role Name: {role['RoleName']}, ARN: {role['Arn']}, Creation Date: {role['CreateDate']}")

            return roles

        except Exception as e:
            print(f"An error occurred: {e}")
            return []

