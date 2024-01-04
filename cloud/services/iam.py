import boto3, logging
import json
from typing import Optional
from cloud.entities.enums import AWSRegions, Service, Policy

# ----------------------------------------------

class IAMAWS:
    def __init__(self, region : AWSRegions):
        self.region : str = region.value
        self.client = boto3.client('iam', region_name=self.region)


    def create_iam(self, role_name: str, policy_arns: list[Policy], service : Service):
        try:
            trust_relationship = self.get_trust_relationship(service)
            if trust_relationship is None:
                raise ValueError(f'Could not find trust relationship for service {service}')

            self.client.create_role(RoleName=role_name,AssumeRolePolicyDocument=json.dumps(trust_relationship))
            for policy_arn in policy_arns:
                self.client.attach_role_policy(RoleName=role_name,PolicyArn=policy_arn.value)
            logging.info(f"IAM Role created: {role_name}")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None


    def create_instance_profile(self, profile_name: str, role_name: str):
        try:
            response = self.client.create_instance_profile(InstanceProfileName=profile_name)
            instance_profile_arn = response['InstanceProfile']['Arn']
            logging.info(f"Instance profile created: {profile_name}")

            self.client.add_role_to_instance_profile(InstanceProfileName=profile_name,RoleName=role_name)
            logging.info(f"Role '{role_name}' attached to instance profile '{profile_name}'")

            return instance_profile_arn

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None

    # ----------------------------------------------
    # get

    @staticmethod
    def get_trust_relationship(service : Service) -> Optional[dict]:
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

            logging.info(f'Found the following roles')
            for role in roles:
                logging.info(f"Role Name: {role['RoleName']}, ARN: {role['Arn']}, Creation Date: {role['CreateDate']}")

            return roles

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return []

    def get_instance_profiles(self) -> list[dict]:
        try:
            response = self.client.list_instance_profiles()
            instance_profiles = response.get('InstanceProfiles', [])

            logging.info(f'Found the following instance profiles:')
            for profile in instance_profiles:
                logging.info(f"Profile Name: {profile['InstanceProfileName']}, ARN: {profile['Arn']}, Creation Date: {profile['CreateDate']}")

            return instance_profiles

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return []