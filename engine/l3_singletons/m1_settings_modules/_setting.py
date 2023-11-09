from __future__ import annotations
import ast
from typing import Optional
import boto3
import json

# (10.10.23) D.H. : Settings Terminology
# -> There is a settings resource either locally on the computer or in the cloud
# -> The setup method of the Settings Controller completes only when valid values are obtained for every setting listed
# -> Values are validated by the _tests defined in each SettingsGrouping

# (10.10.23) D.H. : Settings Workflow
# -> If valid values can be retrieved from the settings resource they are loaded up and the setup terminates
# -> If not, the user will be informed for which settings valid values could not be obtained and be asked if he wants to retry
#  via a y/n prompt
# -> If the user does choose to retry he will be asked to enter new values for the settings that failed to validate
# -> When all settings are valid or the user declines to enter new values on the y/n prompt the setup process terminates


# NOTE : Because everything is saved in a single file, setting labels must be unique
# and so must the name of SettingGroupings  also must be unique

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
            print(f'An error occurred while trying to read value from AWS: {e}')


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
