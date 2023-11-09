from __future__ import annotations
import boto3
from typing import Optional, List
from botocore.exceptions import ClientError

from deploy.cloud.enums import AWSRegions, EC2Type, AMI, InstanceState


class InstanceTemplate:
    def __init__(self, image_id: AMI, ec2_type: EC2Type, setup_script: str = '') -> None:
        self.image_id: str = image_id.value
        self.ec2_type: str = ec2_type.value
        self.setup_script: Optional[str]  = setup_script

    @classmethod
    def make_default(cls) -> InstanceTemplate:
        new_instance = cls(image_id=AMI.UBUNTU_2204, ec2_type=EC2Type.T3_MICRO)
        return new_instance

# ----------------------------------------------


class CloudManager:
    def __init__(self, region: AWSRegions) -> None:
        self.region: str = region.value
        self.ec2_client = boto3.client('ec2', region_name=self.region)
        self.elb_client = boto3.client('elbv2', region_name=self.region)
        self.dynamodb_client = boto3.client('dynamodb', region_name=self.region)

    # ----------------------------------------------
    # EC2 management


    def get_number_of_running_instances(self) -> int:
        try:
            response = self.ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            running_instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]
            return len(running_instances)

        except Exception as e:
            print(f"An error occurred: {e}")
            return 0

    def shutdown_all_instances(self) -> None:
        instances = self._get_all_instance_ids()
        if instances:
            self.ec2_client.stop_instances(InstanceIds=instances)
            print(f"Stopping instances: {instances}")
            self.wait(instance_ids=instances, instance_state=InstanceState.STOPPED)


    def reach_number_of_instances(self, desired_count: int) -> None:
        instances = self._get_all_instance_ids()
        num_running_instances = len(instances)

        self.start_all_instances()
        if num_running_instances < desired_count:
            missing_instances = desired_count-num_running_instances
            self.launch_instances(num=missing_instances)
            print(f"Started additional instances to reach {desired_count}")


    def start_all_instances(self) -> None:
        instance_ids = self._get_all_instance_ids()
        if instance_ids:
            self.ec2_client.start_instances(InstanceIds=instance_ids)
            print(f"Starting instances: {instance_ids}")
            self.wait(instance_ids=instance_ids, instance_state=InstanceState.RUNNING)
        else:
            print(f'No instances found')


    def launch_instances(self,num: int, instance: InstanceTemplate = InstanceTemplate.make_default()):
        try:
            response = self.ec2_client.run_instances(
                ImageId=instance.image_id,
                MinCount=num,
                MaxCount=num,
                InstanceType=instance.ec2_type,
                UserData=instance.setup_script,
            )

            instance_ids = [inst['InstanceId'] for inst in response['Instances']]
            print(f"Launching instances: {instance_ids}")
            self.wait(instance_ids=instance_ids, instance_state=InstanceState.RUNNING)

        except Exception as e:
            print(f"An error occurred: {e}")


    def _get_all_instance_ids(self) -> List[str]:
        try:
            response = self.ec2_client.describe_instances()
            instances = [instance['InstanceId'] for reservation in response['Reservations'] for instance in reservation['Instances'] if instance['State']['Name'] in ['running', 'stopped']]
            return instances
        except ClientError as e:
            print(f"An error occurred: {e}")
            return []


    def wait(self, instance_ids: List[str], instance_state: InstanceState) -> None:
        instance_state_val = instance_state.value
        if not instance_ids:
            print("No instance IDs provided.")
            return

        waiter = self.ec2_client.get_waiter(instance_state_val)
        try:
            print(f"Waiting for instances to be in the '{instance_state_val}' state...")
            waiter.wait(InstanceIds=instance_ids)
            print(f"Instances are now in the '{instance_state_val}' state.")

        except ClientError as e:
            print(f"An error occurred: {e}")


    # ----------------------------------------------
    # Database management

cloud_manager = CloudManager(region=AWSRegions.EU_NORTH_1)
print(f'Currently running instances: {cloud_manager.get_number_of_running_instances()}')
# cloud_manager.start_all_instances()
# cloud_manager.shutdown_all_instances()
# cloud_manager.reach_number_of_instances(desired_count=5)
# cloud_manager.shutdown_all_instances()
# print(f'Currently running instances: {cloud_manager.get_number_of_running_instances()}')