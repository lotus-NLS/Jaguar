import openai
import requests
import os
from typing import Optional

from func_timeout import func_timeout, FunctionTimedOut
from hollarek.cloud import AWSRegion
from hollarek.configs import LocalConfigs, AWSConfigs, Configs
from hollarek.abstract import Singleton
from hollarek.core.logging import LogLevel, get_logger, Logger
# --------------------------------------------

class LotusSettings(Singleton):
    def __init__(self, use_local : bool = False, validate : bool = True, logger : Optional[Logger] = None):
        if self.get_is_initialized():
            return

        super().__init__()
        self.log = logger.log if logger else get_logger().log
        self.configs = self.get_configs(use_local=use_local)
        if validate:
            self.validation()

        self.log(msg=f'Completed setup for all Settings')

    @staticmethod
    def get_configs(use_local : bool) -> Configs:
        if use_local:
            config_path = os.path.join(os.path.expanduser('~'), '.creds', 'lotusconfigs')
            configs = LocalConfigs(config_fpath=config_path)
        else:
            configs = AWSConfigs(secret_name='lotus_api_keys', region=AWSRegion.EU_NORTH_1.value)
        return configs

    @classmethod
    def get_openai_apikey(cls) -> str:
        return cls.get('openai_api_key')

    @classmethod
    def get_google_apikey(cls) -> str:
        return cls.get('google_api_key')

    @classmethod
    def get_searchengine_id(cls) -> str:
        return cls.get('search_engine_id')

    @classmethod
    def get_enable_introduction(cls) -> str:
        return cls.get('enable_introduction')

    @classmethod
    def get(cls, key: str) -> str:
        instance = cls.get_instance()
        if not instance.configs:
            raise ResourceWarning(f'Lotus Settings is not initialized yet!')
        return instance.configs.get(key)


    # ----------------------------------------------
    # validation

    def validation(self):
        successful_tests = []
        failed_tests = []
        for test in [self.validate_openai]:
            if not test():
                failed_tests.append(test.__name__)
            else:
                successful_tests.append(test.__name__)

        if failed_tests:
            raise ValueError(f'Validation failed for {failed_tests}')

        self.log(msg=f'Successfully performed validations {successful_tests}')


    def validate_openai(self) -> bool:
        temp = openai.api_key
        is_successful = False
        err_details = ''
        timeout = 5

        try:
            openai.api_key = self.get_openai_apikey()
            test_entry = {'role' : 'user', 'content' : 'This is a test'}
            args_dict = {'model': 'gpt-3.5-turbo','messages': [test_entry],'stream' : True}
            func_timeout(timeout=timeout, func=openai.chat.completions.create, kwargs=args_dict)
            is_successful = True
        except FunctionTimedOut:
            err_details = f'Request to OpenAI servers timed out after {timeout}'
        except BaseException as err:
            err_details = f'{err}'
        finally:
            if not is_successful:
                self.log(msg=f'Error after test run of openai_api_key: {err_details}', level=LogLevel.ERROR)
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
            response_json = response.model_dump_json()


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
                self.log(msg=f'Error after test run of search engine: {err_details}', level=LogLevel.ERROR)
            return is_successful


