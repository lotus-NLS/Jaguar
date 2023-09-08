from __future__ import annotations

import time
from typing import Union
import openai
import os
import configparser
import requests

# New m1_settings workflow:
# Issue: Cannot always test individual m1_settings, therefore
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

    def save_state_to_file(self):
        try:
            if self.section not in config_parser.sections():
                config_parser.add_section(self.section)
            config_parser.set(section=self.section,option=self.label,value=self.value)
            with open(config_path,'w') as f:
                config_parser.write(f)
            print(f'[Debug]: Saved give value for setting {self.label} to settings file')

        except Exception as e:
            print(f'[Error]: An exception occured while trying to save setting {self.label}: {e}')


    def try_setup_from_file(self):
        try:
            self.set_value(is_from_file=True)
        except Exception as e:
            print(
                f'[Error]: An error occured while trying to obtain valid setting value for setting {the_setting.label} from settings file: {e}')
            self.set_value(is_from_file=False)
        time.sleep(0.1)


    def setup_from_user_input(self):
        self.set_value(is_from_file=False)

    # --------------------------------------------
    # get

    def get_is_validated(self) -> bool:
        return self._is_validated

    def set_value(self, is_from_file : bool) -> None:
        if is_from_file:
            config_parser.read(config_path)
            self.value = config_parser.get(self.section, self.label)

        else:
            self.value = input(f'Enter value for setting {self.label}\n')


class SettingGrouping:
    all_settings = []

    def setup(self):
        pass

    @staticmethod
    def get_validated_settings() -> list[Setting]:
        return [setting for setting in CredentialSettings.all_settings if setting.get_is_validated()]

    @staticmethod
    def get_non_validated_settings() -> list[Setting]:
        return [setting for setting in CredentialSettings.all_settings if not setting.get_is_validated()]


class CredentialSettings(SettingGrouping):
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
    def get_y_or_n(msg : str):
        while True:
            user_input = input(msg)
            if user_input.lower() in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")

        return user_input


    def setup(self, is_first_run = True) -> None:
        for the_setting in self.get_non_validated_settings():
            the_setting.try_setup_from_file() if is_first_run else the_setting.setup_from_user_input()

        for test in self.tests:
            try:
                test()
            except Exception as e:
                print(f'[Error]: An error occured while performing test {test.__name__}: {e}')

        for setting in self.get_validated_settings():
            setting.save_state_to_file()

        non_validated_settings = self.get_non_validated_settings()
        count_non_validated_settings = len(non_validated_settings)
        if not count_non_validated_settings == 0:
            msg = f'[Error]: {count_non_validated_settings} setting(s) failed to validate. Retry setup for those settings? (y/n) \n'
            if self.get_y_or_n(msg) == 'y':
                self.setup(is_first_run=False)


    def openai_apikey_test(self) -> None:
        temp = openai.api_key

        try:
            openai.api_key = self.openai_apikey_setting.value
            args_dict = {
                'model': 'gpt-3.5-turbo',
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


# TODO : The settings (through the SettingManager) be must be exposed with read only access to all but the run module, else it has the characteristic of a variable global to the whole project
# It works as it is now but the price is heavy redundancies (at least 4 (!) instances of EACH settings mention are redundant
class SettingManager:
    def __init__(self):
        self.credential_settings : Union[None, CredentialSettings] = CredentialSettings()

    def setup(self) -> None:
        self.credential_settings.setup()
        print(f'[Debug]: Completed setup for all Settings')

    def get_openai_apikey(self):
        return self.credential_settings.openai_apikey_setting.value

    def get_google_apikey(self):
        return self.credential_settings.google_apikey_setting.value

    def get_searchengine_id(self):
        return self.credential_settings.search_engineID_setting.value


the_settings_manager = SettingManager()
get_openai_apikey = the_settings_manager.get_openai_apikey
get_google_apikey = the_settings_manager.get_google_apikey
get_searchengine_id = the_settings_manager.get_searchengine_id

