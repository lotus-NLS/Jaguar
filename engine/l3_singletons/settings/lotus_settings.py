from func_timeout import func_timeout
import logging
import openai
import requests
from .categories import Categories
from hollarek.io import ConfigManager

# --------------------------------------------

class LotusSettings:
    def __init__(self, use_local : bool = False):
        self.use_local = use_local
        self.config_manager = ConfigManager()


    def get_openai_apikey(self) -> str:
        return self.get_value(key='openai_apikey', category=Categories.CRED)

    def get_google_apikey(self) -> str:
        return self.get_value(key='google_apikey', category=Categories.CRED)

    def get_searchengine_id(self) -> str:
        return self.get_value(key='searchengine_id', category=Categories.CRED)

    def get_enable_introduction(self) -> str:
        return self.get_value(key='enable_introduction', category=Categories.DIALOG)

    def get_value(self, key : str, category : Categories) -> str:
        pass

    # ----------------------------------------------
    # validation


    def setup(self, perform_validation = True):
        if perform_validation:
            self.test_openai_apikey()
            self.test_search_engine()
        logging.info(f'Completed setup for all Settings')


    def test_openai_apikey(self) -> bool:
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
            err_details = f'Invalid API key or no internet connection\n{err} '

        finally:
            if not is_successful:
                logging.error(f'Error after test run of openai_api_key: {err_details}')

            openai.api_key = temp
            return is_successful


    def test_search_engine(self) -> bool:
        is_successful = False
        err_details = ''
        try:

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': 'snails',
                'key': self.get_google_apikey(),
                'cx': self.get_google_apikey()
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
                logging.error(f'[Error]: Error after test run of search engine: {err_details}')
            return is_successful

