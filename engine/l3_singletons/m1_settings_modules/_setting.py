from __future__ import annotations
import ast
from typing import Optional
import boto3
import json
import logging

# ----------------------------------------------------

# AWS
secret_name = "lotus_api_keys"
region_name = "eu-north-1"

class Setting:
    def __init__(self, label : str, section : str, dtype : type):
        self.label : str = label
        self.section : str = section
        self.dtype : type = dtype
        self.value: Optional[dtype] = None

        self._is_functional : bool = False



    def get_is_functional(self) -> bool:
        return self._is_functional

    # --------------------------------------------
    # Setup value

    def set_value(self):
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            secrets = json.loads(get_secret_value_response['SecretString'])
            value_str = secrets.get(self.label, '')
            self.value = self.get_typecast_value(value_str=value_str)

        except Exception as e:
            logging.error(f'An error occurred while trying to read value from AWS: {e}')


    def get_typecast_value(self, value_str : str) -> Optional[object]:
        if self.dtype is str:
            return value_str

        value = None
        try:
            eval_value = ast.literal_eval(value_str)
            cast_value = self.dtype(eval_value)

            if eval_value == cast_value:
                value = cast_value

        finally:
            return value


    def validate_functionality(self):
        self._is_functional = True
