import boto3, logging
from cloud.entities.enums import AWSRegions

# ----------------------------------------------

class DatabaseAWS:
    def __init__(self, region : AWSRegions):
        self.region : str = region.value
        self.dynamodb_client = boto3.client('dynamodb', region_name=self.region)


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
            self.wait_for_dynamodb_action(table_name=table_name, waiter_type='table_exists')

        except:
            logging.error(f'An error occurred while creating table {table_name}')


    def wait_for_dynamodb_action(self, table_name: str, waiter_type: str) -> None:
        try:
            logging.info(f"Waiting for '{waiter_type}' action on table '{table_name}'...")
            waiter = self.dynamodb_client.get_waiter(waiter_type)
            waiter.wait(TableName=table_name)
            logging.info(f"Action '{waiter_type}' completed on table '{table_name}'.")
        except Exception as e:
            logging.error(f"An error occurred while waiting for '{waiter_type}' action: {e}")
