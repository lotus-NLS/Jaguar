from __future__ import annotations
import openai
import requests

from src.l3_lotus_core.m0_settings._setting import Setting
from src.l3_lotus_core.m0_settings._setting_grouping import SettingGrouping, SettingTest

# ---------------------------------------------------------

class CredentialSettings(SettingGrouping):
    openai_apikey_label = 'openai_api_key'
    google_apikey_label = 'google_api_key'
    search_engineID_label = 'search_engine_id'

    def __init__(self):
        super(CredentialSettings, self).__init__()

        self.openai_apikey_test = SettingTest(test_body=self.test_openai_apikey)
        self.search_engine_test = SettingTest(test_body=self.test_search_engine)

        self.openai_apikey_setting : Setting = self.make_setting(label=CredentialSettings.openai_apikey_label,
                                                                 test=self.openai_apikey_test)

        self.google_apikey_setting : Setting = self.make_setting(label=CredentialSettings.google_apikey_label,
                                                                 test=self.search_engine_test)

        self.search_engineID_setting : Setting = self.make_setting(label=CredentialSettings.search_engineID_label,
                                                                   test=self.search_engine_test)

    # ---------------------------------------------------------
    # Tests

    def set_tests(self):
        self.tests = [self.openai_apikey_test,self.search_engine_test]


    def test_openai_apikey(self) -> bool:
        temp = openai.api_key
        is_successful = False

        try:
            openai.api_key = self.openai_apikey_setting.value
            args_dict = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role' : 'user', 'content' : 'This is a test'}]
            }
            openai.ChatCompletion.create(**args_dict)
            is_successful = True

        except Exception as err:
            print(f'[Debug]: Error after test run:\n{err}')
            raise ValueError('Invalid API key or no internet connection')

        finally:
            openai.api_key = temp
            return is_successful


    def test_search_engine(self) -> bool:
        is_successful = False
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': 'snails',
                'key': self.google_apikey_setting,
                'cx': self.search_engineID_setting
            }
            response = requests.get(url, params=params)
            _ = response.json()

            is_successful = True

        except Exception as err:
            print(f'[Error]: Error after test run of search engine \n {err}')
            raise ValueError(f'Invalid {self.search_engineID_setting.label} or {self.google_apikey_setting} or no internet connection')

        finally:
            return is_successful