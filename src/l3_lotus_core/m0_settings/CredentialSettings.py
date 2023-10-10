from __future__ import annotations
import openai
import requests

from src.l3_lotus_core.m0_settings._setting import Setting
from src.l3_lotus_core.m0_settings._setting_grouping import SettingGrouping

# ---------------------------------------------------------

class CredentialSettings(SettingGrouping):
    openai_apikey_label = 'openai_api_key'
    google_apikey_label = 'google_api_key'
    search_engineID_label = 'search_engine_id'

    def __init__(self):
        super(CredentialSettings, self).__init__(tests=[self.openai_apikey_test, self.search_engine_test])
        self.openai_apikey_setting : Setting = self.make_setting(label=CredentialSettings.openai_apikey_label)
        self.google_apikey_setting : Setting = self.make_setting(label=CredentialSettings.google_apikey_label)
        self.search_engineID_setting : Setting = self.make_setting(label=CredentialSettings.search_engineID_label)


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
