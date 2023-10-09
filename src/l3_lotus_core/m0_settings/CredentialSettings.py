from __future__ import annotations

import openai
import requests

from src.l3_lotus_core.m1_OperatorIO.userIO import user_io
from src.l3_lotus_core.m0_settings.setting import SettingGrouping, Setting


class CredentialSettings(SettingGrouping):
    openai_apikey_label = 'openai_api_key'
    google_apikey_label = 'google_api_key'
    search_engineID_label = 'search_engine_id'

    def __init__(self):
        super(CredentialSettings, self).__init__(tests=[self.openai_apikey_test, self.search_engine_test])
        self.openai_apikey_setting : Setting = self.make_setting(label=CredentialSettings.openai_apikey_label)
        self.google_apikey_setting : Setting = self.make_setting(label=CredentialSettings.google_apikey_label)
        self.search_engineID_setting : Setting = self.make_setting(label=CredentialSettings.search_engineID_label)


    def setup(self, is_first_run = True, is_perform_validation = True):
        for the_setting in self.get_non_validated_settings():
            the_setting.try_setup_from_file() if is_first_run else the_setting.setup_from_user_input()

        if is_perform_validation:
            self.test_all()
        else:
            self.pass_all()

        for setting in self.get_validated_settings():
            setting.save_state_to_file()

        non_validated_settings = self.get_non_validated_settings()
        count_non_validated_settings = len(non_validated_settings)
        if not count_non_validated_settings == 0:
            msg = f'[Error]: {count_non_validated_settings} setting(s) failed to validate. Retry setup for those settings? (y/n) \n'
            if user_io.get_confirmation(msg=msg):
                self.setup(is_first_run=False)


    def openai_apikey_test(self):
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
