import boto3
from .enums import AWSRegions
import io
import zipfile

# ----------------------------------------------

class LambdaManager:
    def __init__(self, region : AWSRegions):
        self.region : str = region.value
        self.lambda_client = boto3.client('lambda', region_name=self.region)


    def deploy_lambda_function(self, lambda_name: str, role_arn: str, handler: str, module_code: str):
        try:

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