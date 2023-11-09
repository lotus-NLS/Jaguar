from .manager import CloudManager
from .enums import AWSRegions

# ----------------------------------------------
# EC2 management

cloud_manager = CloudManager(region=AWSRegions.EU_NORTH_1)
# cloud_manager.create_lambda_iam(role_name='MyLambdaRole4'
#                                 ,policy_arns=['arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
#                                               'arn:aws:iam::aws:policy/SecretsManagerReadWrite'])
# cloud_manager.get_iam_roles()

function_name = "MyGitHubBackupFunction9"
role_arn = "arn:aws:iam::139384887340:role/MyLambdaRole4"
handler = "backup_repo.backup_github_repo"

with open('/home/daniel/Lotus/deploy/cloud/backup_repo.py') as f:
    module_code = f.read()

cloud_manager.deploy_lambda_function(function_name, role_arn, handler,module_code)


# cloud_manager.shutdown_all_instances()
# print(f'Currently running instances: {cloud_manager.get_number_of_running_instances()}')
# cloud_manager.start_all_instances()
# cloud_manager.shutdown_all_instances()
# cloud_manager.reach_number_of_instances(desired_count=5)
# cloud_manager.shutdown_all_instances()
# print(f'Currently running instances: {cloud_manager.get_number_of_running_instances()}')
# cloud_manager.create_dynamodb_table()