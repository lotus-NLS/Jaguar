from __future__ import annotations

import time
from typing import Union
import openai
import os
import configparser
import requests

from .constants import Models


# New settings workflow:
# Issue: Cannot always test individual settings, therefore
# -> each Settings group will get its own tests that are performed on setup
# -> Settings will not get invididual test functions, but rather: is_validated attribute

# ---------------------------------------------------------

home = os.path.expanduser("~")
config_path = os.path.join(home, 'settings_[uuid_4d9498a7-2f46-4372-9c49-c96e3c41d4f7].ini')
config_parser = configparser.ConfigParser()



class Setting:
    def __init__(self,label : str, section : str):
        self.label : str = label
        self.section : str = section
        self.value : Union[None, str] = None
        self._is_validated : bool = False

    # --------------------------------------------
    # Setup

    def validate(self):
        self._is_validated = True

    def save(self,value : str):
        try:
            if self.section not in config_parser.sections():
                config_parser.add_section(self.section)
            config_parser.set(self.label, value)
            with open(config_path,'w') as f:
                config_parser.write(f)
            print(f'[Debug]: Saved value {value} for setting {self.label} to settings file')

        except Exception as e:
            print(f'[Error]: An exception occured while trying to save setting {value} for setting {self.label}: {e}')

    # --------------------------------------------
    # get



    def get_is_validated(self) -> bool:
        return self._is_validated

    def set_value(self, is_from_file : bool) -> None:
        if is_from_file:
            config_parser.read(config_path)
            self.value = config_parser.get(self.section, self.label)

        else:
            self.value = input(f'Enter value for setting {self.label}')

# TODO: Make new absctract class: Settings grouping
class CredentialSettings:
    all_settings = []

    def __init__(self):
        def CredentialSetting(label : str) -> Setting:
            new_setting = Setting(label=label, section=CredentialSettings.__name__)
            CredentialSettings.all_settings.append(new_setting)
            return new_setting

        self.openai_apikey_setting : Setting = CredentialSetting(label='openai_api_key')
        self.google_apikey_setting : Setting = CredentialSetting(label='google_api_key')
        self.search_engineID_setting : Setting = CredentialSetting(label='search_engine_id')

        self.tests = [self.openai_apikey_test,self.search_engine_test]

    @staticmethod
    def get_non_validated_settings():
        return [setting for setting in CredentialSettings.all_settings if not setting.get_is_validated()]

    def setup(self) -> None:
        for the_setting in self.get_non_validated_settings():
            try:
                the_setting.set_value(is_from_file=True)
            except Exception as e:
                print(f'[Error]: An error occured while trying to obtain valid setting value from settings file: {e}')
                the_setting.set_value(is_from_file=False)
            time.sleep(0.1)

        for test in self.tests:
            test()

        if not len(self.get_non_validated_settings()) == 0:
            

            self.setup()


    def openai_apikey_test(self) -> None:
        temp = openai.api_key

        try:
            openai.api_key = self.openai_apikey_setting.value
            args_dict = {
                'model': Models.get_test_model(),
                'messages': [{'role' : 'user', 'content' : 'This is a test'}]
            }
            openai.ChatCompletion.create(**args_dict)
            self.openai_apikey_setting.validate()

        except Exception as err:
            print(f'[Debug]: Error after test run:\n{err}')
            raise ValueError('Invalid API key or no internet connection')

        finally:
            openai.api_key = temp


    def search_engine_test(self):
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': 'snails',
                'key': self.google_apikey_setting,
                'cx': self.search_engineID_setting
            }
            response = requests.get(url, params=params)
            _ = response.json()

            self.search_engineID_setting.validate()
            self.google_apikey_setting.validate()

        except Exception as err:
            print(f'[Error]: Error after test run of search engine \n {err}')
            raise ValueError(f'Invalid {self.search_engineID_setting.label} or {self.google_apikey_setting} or no internet connection')



class SettingManager:
    def __init__(self):
        self.credential_settings : Union[None, CredentialSettings] = CredentialSettings()

    def get_credentials(self) -> CredentialSettings:
        return self.credential_settings

