# from pyutils import get_txt_file_content
from cloud.manager import CloudManager
from components import (AWSRegions,
                                           # InstanceTemplate,
                                           # EC2Type,
                                           # ImageID,
                    )


# ----------------------------------------------
# EC2 management

cloud_manager = CloudManager(region=AWSRegions.EU_NORTH_1)

# cloud_manager.iam.create_iam(role_name='BackupLambda3',
#                              policy_arns=[Policy.LAMBDA_BASIC_EXECUTION_ROLE,
#                                           Policy.SECRETS_MANAGER_READ_WRITE,
#                                           Policy.S3_FULL_ACCESS],
#                              service=Service.LAMBDA)
# cloud_manager.iam.get_iam_roles()




from autorun_scripts.backup_repo import do_backup
lambda_role_arn = "arn:aws:iam::139384887340:role/BackupLambda3"
cloud_manager.lambda_aws.cloud_lambda_function(the_function=do_backup, role_arn=lambda_role_arn)

# ----------------------------------------------
# Archive


# EC2 instances
# setup_script = get_txt_file_content(location='autorun_scripts/setup_engine.sh')
# lotus_instance = InstanceTemplate(ec2_type=EC2Type.T3_MICRO,
#                                   image_id=ImageID.UBUNTU_2204,
#                                   setup_script=setup_script,
#                                   key_pair_name='lotus_key',
#                                   instance_name='lotus_from_code',
#                                   instance_profile_arn='arn:aws:iam::139384887340:instance-profile/lotus_instance',
#                                   security_group='sg-04536ba167a51d751')
# cloud_manager.ec2.launch_instanaaaces(num=1, template=lotus_instance)
# LAMBDAS
# cloud_manager.lambda_aws.cloud_lambda_function(function_name, role_arn, handler,module_code)
# This function should simply take the python function object itself and optionally the role_arn
# and just work
# cloud_manager.iam.create_iam(role_name='BackupLambda2',
#                              policy_arns=[Policy.LAMBDA_BASIC_EXECUTION_ROLE, Policy.SECRETS_MANAGER_READ_WRITE],
#                              service=Service.LAMBDA)
# cloud_manager.iam.get_iam_roles()
