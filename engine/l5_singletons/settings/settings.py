import openai
import requests
import os
from typing import Optional

from func_timeout import func_timeout, FunctionTimedOut
from hollarek.configs import LocalConfigs, AWSConfigs
from hollarek.templates import Singleton
from hollarek.logging import LogLevel, get_logger
# --------------------------------------------

class Settings(Singleton):
    configs : Optional = None

    def __init__(self, local : bool = False, validate : bool = True):
        if self.get_is_initialized():
            return

        super().__init__()
        self.log = get_logger().log
        config_path = os.path.join(os.path.expanduser('~'), '.creds' , 'lotusconfigs')
        if local:
            Settings.configs = LocalConfigs(config_fpath=config_path)
        else:
            Settings.configs = AWSConfigs(secret_name='lotus_api_keys')

        if validate:
            self.validate_openai_key()
            self.validate_search_engine()
            self.log(msg=f'All Settings validated')

        self.log(msg=f'Completed setup for all Settings')

    @classmethod
    def get_openai_apikey(cls) -> str:
        return cls.configs.get('openai_api_key')

    @classmethod
    def get_google_apikey(cls) -> str:
        return cls.configs.get('google_api_key')

    @classmethod
    def get_searchengine_id(cls) -> str:
        return cls.configs.get('search_engine_id')

    @classmethod
    def get_enable_introduction(cls) -> str:
        return cls.configs.get('enable_introduction')

    @classmethod
    def get(cls, key: str) -> str:
        return cls.configs.get(key)

    # ----------------------------------------------
    # validation

    def validate_openai_key(self) -> bool:
        temp = openai.api_key
        is_successful = False
        err_details = ''
        timeout = 5

        try:
            openai.api_key = self.get_openai_apikey()
            args_dict = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role' : 'user', 'content' : 'This is a test'}],
                'stream' : True
            }

            func_timeout(timeout=timeout, func=openai.ChatCompletion.create, kwargs=args_dict)
            is_successful = True

        except FunctionTimedOut:
            err_details = f'Request to OpenAI servers timed out after {timeout}'
        except BaseException as err:
            err_details = f'{err}'

        finally:
            if not is_successful:
                self.log(f'Error after test run of openai_api_key: {err_details}', level=LogLevel.ERROR)

            openai.api_key = temp
            return is_successful


    def validate_search_engine(self) -> bool:
        is_successful = False
        err_details = ''
        try:

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': 'snails',
                'key': self.get_google_apikey(),
                'cx': self.get_searchengine_id(),
                'num' : 5
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
                self.log(f'Error after test run of search engine: {err_details}', LogLevel.ERROR)
            return is_successful



