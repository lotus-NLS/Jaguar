from __future__ import annotations
import openai
import requests
from func_timeout import func_timeout

from engine.l3_singletons.m1_settings_modules import Setting,SettingGrouping, SettingTest

# ---------------------------------------------------------

class CredentialSettings(SettingGrouping):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CredentialSettings, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return

        super(CredentialSettings, self).__init__()

        self._openai_apikey_test : SettingTest = SettingTest(test_body=self.test_openai_apikey)
        self._search_engine_test : SettingTest = SettingTest(test_body=self.test_search_engine)

        self._openai_apikey_setting : Setting = self.make_setting(label='openai_api_key', test=self._openai_apikey_test)
        self._google_apikey_setting : Setting = self.make_setting(label='google_api_key', test=self._search_engine_test)
        self._search_engineID_setting : Setting = self.make_setting(label='search_engine_id', test=self._search_engine_test)

        self.__initialized = True
    # ---------------------------------------------------------
    # Retrieve Settings

    def get_openai_key(self):
        return self._openai_apikey_setting.value

    def get_google_apikey(self):
        return self._google_apikey_setting.value

    def get_searchengine_ID(self):
        return self._search_engineID_setting.value

    # ---------------------------------------------------------
    # Tests

    def test_openai_apikey(self) -> bool:
        temp = openai.api_key
        is_successful = False
        err_details = ''

        try:
            openai.api_key = self._openai_apikey_setting.value
            args_dict = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role' : 'user', 'content' : 'This is a test'}],
                'stream' : True
            }

            func_timeout(timeout=5, func=openai.ChatCompletion.create, kwargs=args_dict)
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
                'key': self._google_apikey_setting.value,
                'cx': self._search_engineID_setting.value
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