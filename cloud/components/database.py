import boto3
from .enums import AWSRegions

# ----------------------------------------------

class DatabaseManager:
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

            print(f"Table creation initiated: {table_name}")
            waiter = self.dynamodb_client.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print(f"Table created: {table_name}")
        except Exception as e:
            print(f"An error occurred: {e}")