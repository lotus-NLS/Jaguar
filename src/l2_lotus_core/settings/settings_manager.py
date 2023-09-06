from __future__ import annotations

import time
from typing import Union
import openai
import os
import configparser

from .constants import Models
# ---------------------------------------------------------

home = os.path.expanduser("~")
config_path = os.path.join(home, 'settings_[uuid_4d9498a7-2f46-4372-9c49-c96e3c41d4f7].ini')
config_parser = configparser.ConfigParser()



class Setting:
    all_settings : list[Setting] = []

    def __init__(self,label : str, section : str):
        self._label : str = label
        self._section : str = section
        self._value : Union[None, str] = None
        self._raise_error_if_invalid : callable = lambda *args, **kwargs: None

        Setting.all_settings.append(self)

    # --------------------------------------------
    # Setup

    def set_test(self, test_function) -> None:
        self._raise_error_if_invalid = test_function

    def register_value(self, value : str) -> None:
        self._value = value

    def save(self,value : str):
        try:
            if self._section not in config_parser.sections():
                config_parser.add_section(self._section)
            config_parser.set(self._label, value)
            with open(config_path,'w') as f:
                config_parser.write(f)
            print(f'[Debug]: Saved value {value} for setting {self._label} to settings file')

        except Exception as e:
            print(f'[Error]: An exception occured while trying to save setting {value} for setting {self._label}: {e}')

    # --------------------------------------------
    # get

    def get_is_set_up(self):
        return not self._value is None

    def get_valid_value(self, is_from_file : bool) -> str:
        if is_from_file:
            config_parser.read(config_path)
            value = config_parser.get(self._section, self._label)

        else:
            value = input(f'Enter value for setting {self._label}')

        self._raise_error_if_invalid(value)
        return value


class CredentialSettings:
    def __init__(self):
        CredentialSetting = lambda label : Setting(label=label, section=CredentialSettings.__name__)

        self.openai_apikey : Setting = CredentialSetting(label='openai_api_key')
        self.google_api_key : Setting = CredentialSetting(label='google_api_key')
        self.search_engine_id : Setting = CredentialSetting(label='search_engine_id')

        self.openai_apikey.set_test(test_function=openai_apikey_test)


def openai_apikey_test(key : str) -> None:
    try:
        openai.api_key = key
        args_dict = {
            'model': Models.get_test_model(),
            'messages': [{'role' : 'user', 'content' : 'This is a test'}]
        }
        openai.ChatCompletion.create(**args_dict)

    except Exception as err:
        print(f'[Debug]: Error after test run:\n{err}')
        raise ValueError('Invalid API key')


class SettingManager:
    def __init__(self):
        self.credential_settings : Union[None, CredentialSettings] = CredentialSettings()

    def get_credentials(self) -> CredentialSettings:
        return self.credential_settings

    @staticmethod
    def setup(self) -> None:
        def try_set_valid_value(setting : Setting) -> None:
            try:
                value = setting.get_valid_value(is_from_file=True)
            except Exception as e:
                print(f'[Error]: An error occured while trying to obtain valid setting value from settings file: {e}')
                value = setting.get_valid_value(is_from_file=False)

            setting.save(value=value)
            setting.register_value(value=value)

        for the_setting in Setting.all_settings:
            while the_setting._value is None:
                try_set_valid_value(the_setting)
                time.sleep(0.1)