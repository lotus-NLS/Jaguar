from pyutils import get_txt_file_content
from deploy.cloud.manager import CloudManager
from deploy.cloud.components.enums import AWSRegions, InstanceTemplate, EC2Type, ImageID, ServiceURL


# ----------------------------------------------
# EC2 management

cloud_manager = CloudManager(region=AWSRegions.EU_NORTH_1)

setup_script = get_txt_file_content(location='autorun_scripts/setup.sh')
lotus_instance = InstanceTemplate(ec2_type=EC2Type.T3_MICRO,
                                  image_id=ImageID.UBUNTU_2204,
                                  setup_script=setup_script,
                                  key_pair_name='lotus_key',
                                  instance_name='lotus_from_code',
                                  instance_profile_arn='arn:aws:iam::139384887340:instance-profile/lotus_instance',
                                  security_group='sg-04536ba167a51d751')
cloud_manager.ec2.launch_instances(num=1, template=lotus_instance)


# function_name = "MyGitHubBackupFunction9"
# role_arn = "arn:aws:iam::139384887340:role/MyLambdaRole4"
# handler = "backup_repo.backup_github_repo"
#
# with open('/deploy/cloud/components/backup_repo.py') as f:
#     module_code = f.read()
#
# cloud_manager.lambda_aws.deploy_lambda_function(function_name, role_arn, handler,module_code)
