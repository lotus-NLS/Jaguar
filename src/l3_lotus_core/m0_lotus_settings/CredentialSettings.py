from __future__ import annotations
import openai
import requests

from src.l3_lotus_core.m1_settings_modules import Setting
from src.l3_lotus_core.m1_settings_modules import SettingGrouping, SettingTest

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


    def test_openai_apikey(self) -> bool:
        temp = openai.api_key
        is_successful = False
        err_details = ''

        try:
            openai.api_key = self.openai_apikey_setting.value
            args_dict = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role' : 'user', 'content' : 'This is a test'}]
            }
            openai.ChatCompletion.create(**args_dict)
            is_successful = True

        except Exception as err:
            err_details = f'Invalid API key or no internet connection\n{err} '

        finally:
            if not is_successful:
                print(f'[Error]: Error after test run of openai_api_key: {err_details}')

            openai.api_key = temp
            return is_successful


    def test_search_engine(self) -> bool:
        is_successful = False
        err_details = ''
        try:

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': 'snails',
                'key': self.google_apikey_setting.value,
                'cx': self.search_engineID_setting.value
            }
            response = requests.get(url, params=params)
            response_json = response.json()

            is_successful = response.status_code == 200
            if 'error' in response_json:
                error_info = response_json['error']
                err_details = f"Google API Error: {error_info.get('message', 'Unknown error')}"
            else:
                err_details = f"Received unexpected status code {response.status_code}"

        except Exception as err:
            err_details = f'Google services could not be reached. Is internet connection available? {err}'

        finally:
            if not is_successful:
                print(f'[Error]: Error after test run of search engine: {err_details}')
            return is_successful