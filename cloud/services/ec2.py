import boto3, logging
from botocore.exceptions import ClientError
from typing import List

from cloud.entities.EC2Template import InstanceTemplate
from cloud.entities.enums import AWSRegions, InstanceState

# ----------------------------------------------

class EC2AWS:
    def __init__(self, region : AWSRegions):
        self.region : str = region.value
        self.ec2_client  = boto3.client('ec2', region_name=region.value)

    # ----------------------------------------------
    # set

    def launch_instances(self, num: int, template: InstanceTemplate = InstanceTemplate.make_default()):
        params = template.get_params(num=num)

        try:
            response = self.ec2_client.run_instances(**params)
            instance_ids = [inst['InstanceId'] for inst in response['Instances']]
            logging.info(f"Launching instances: {instance_ids}")
            self.wait(instance_ids=instance_ids, instance_state=InstanceState.RUNNING)

        except Exception as e:
            logging.error(f"An error occurred: {e}")


    def shutdown_all_instances(self) -> None:
        instances = self.get_all_instance_ids()
        if instances:
            self.ec2_client.stop_instances(InstanceIds=instances)
            logging.info(f"Stopping instances: {instances}")
            self.wait(instance_ids=instances, instance_state=InstanceState.STOPPED)


    def reach_number_of_instances(self, desired_count: int) -> None:
        instances = self.get_all_instance_ids()
        num_running_instances = len(instances)

        self.start_all_instances()
        if num_running_instances < desired_count:
            missing_instances = desired_count - num_running_instances
            self.launch_instances(num=missing_instances)
            logging.info(f"Started additional instances to reach {desired_count}")


    def start_all_instances(self) -> None:
        instance_ids = self.get_all_instance_ids()
        if instance_ids:
            self.ec2_client.start_instances(InstanceIds=instance_ids)
            logging.info(f"Starting instances: {instance_ids}")
            self.wait(instance_ids=instance_ids, instance_state=InstanceState.RUNNING)
        else:
            logging.info(f'No instances found')

    # ----------------------------------------------
    # get

    def get_number_of_running_instances(self) -> int:
        try:
            response = self.ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            running_instances = [instance for reservation in response['Reservations'] for instance in
                                 reservation['Instances']]
            return len(running_instances)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return 0


    def get_all_instance_ids(self) -> List[str]:
        try:
            response = self.ec2_client.describe_instances()
            instances = [instance['InstanceId'] for reservation in response['Reservations'] for instance in
                         reservation['Instances'] if instance['State']['Name'] in ['running', 'stopped']]
            return instances
        except ClientError as e:
            logging.error(f"An error occurred: {e}")
            return []

    # ----------------------------------------------
    # Other

    def wait(self, instance_ids: List[str], instance_state: InstanceState) -> None:
        instance_state_val = instance_state.value
        if not instance_ids:
            logging.info("No instance IDs provided.")
            return

        waiter = self.ec2_client.get_waiter(instance_state_val)
        try:
            logging.info(f"Waiting for instances to be in the '{instance_state_val}' state...")
            waiter.wait(InstanceIds=instance_ids)
            logging.info(f"Instances are now in the '{instance_state_val}' state.")

        except ClientError as e:
            logging.info(f"An error occurred: {e}")


