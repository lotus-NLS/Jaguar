from __future__ import annotations
import boto3
import json
from deploy.cloud.components.enums import AWSRegions
from deploy.cloud.components.ec2 import EC2Manger

# ----------------------------------------------

class CloudManager:
    def __init__(self, region: AWSRegions) -> None:
        self.region: str = region.value
        self.ec2 : EC2Manger = EC2Manger(region=region)

        self.elb_client = boto3.client('elbv2', region_name=self.region)
        self.dynamodb_client = boto3.client('dynamodb', region_name=self.region)
        self.lambda_client = boto3.client('lambda', region_name=self.region)
        self.events_client = boto3.client('events', region_name=self.region)
        self.iam_client = boto3.client('iam',region_name=self.region)

    # ----------------------------------------------
    # Database management

    def create_dynamodb_table(self, table_name: str,
                              key_schema: list,
                              attribute_definitions: list,
                              provisioned_throughput: dict) -> None:
        try:
            response = self.dynamodb_client.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput
            )
            _ = response

            print(f"Table creation initiated: {table_name}")
            waiter = self.dynamodb_client.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print(f"Table created: {table_name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # ----------------------------------------------
    # Lambda management

    def deploy_lambda_function(self, lambda_name: str, role_arn: str, handler: str, module_code: str):
        try:
            import io
            import zipfile

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr('backup_repo.py', module_code)


            response = self.lambda_client.create_function(
                FunctionName=lambda_name,
                Runtime='python3.10',
                Role=role_arn,
                Handler=handler,
                Code={'ZipFile': zip_buffer.getvalue()},
            )

            print(f"Lambda function deployed: {lambda_name}")
            return response['FunctionArn']

        except Exception as e:
            print(f"An error occurred: {e}")


    # def schedule_lambda_backup(self, function_arn: str, schedule_expression: str):
    #     try:
    #         rule_response = self.events_client.put_rule(
    #             Name='github_backup_rule',
    #             ScheduleExpression=schedule_expression,  # e.g., 'rate(1 day)'
    #             State='ENABLED',
    #         )
    #
    #         self.events_client.put_targets(
    #             Rule='github_backup_rule',
    #             Targets=[{'Id': '1', 'Arn': function_arn}]
    #         )
    #
    #         print(f"Scheduled Lambda for GitHub backups with rule: {rule_response['RuleArn']}")
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    # ----------------------------------------------

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

