import openai
import requests
import os

from func_timeout import func_timeout
from hollarek.io import LocalConfigs, AWSConfigs
from hollarek.tmpl import Loggable, LogLevel
# --------------------------------------------

class LotusSettings(Loggable):
    def __init__(self, local : bool = False, validate : bool = True):
        super().__init__()
        config_path = os.path.join(os.path.expanduser('~'), '.creds' , 'lotusconfigs')
        if local:
            self.configs = LocalConfigs(config_fpath=config_path)
        else:
            self.configs = AWSConfigs(secret_name='lotus_api_keys')

        if validate:
            try:
                self.validate_openai_key()
                self.validate_search_engine()
                self.log(f'All Settings validated')
            except:
                self.log(f'Error validating settings', level=LogLevel.ERROR)

        self.log(f'Completed setup for all Settings')


    def get_openai_apikey(self) -> str:
        return self.configs.get(key='openai_api_key')

    def get_google_apikey(self) -> str:
        return self.configs.get(key='google_api_key')

    def get_searchengine_id(self) -> str:
        return self.configs.get(key='search_engine_id')

    def get_enable_introduction(self) -> str:
        return self.configs.get(key='enable_introduction')

    def get(self, key : str) -> str:
        return self.configs.get(key=key)

    # ----------------------------------------------
    # validation

    def validate_openai_key(self) -> bool:
        temp = openai.api_key
        is_successful = False
        err_details = ''

        try:
            openai.api_key = self.get_openai_apikey()
            args_dict = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role' : 'user', 'content' : 'This is a test'}],
                'stream' : True
            }

            func_timeout(timeout=5, func=openai.ChatCompletion.create, kwargs=args_dict)
            is_successful = True

        except Exception as err:
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



