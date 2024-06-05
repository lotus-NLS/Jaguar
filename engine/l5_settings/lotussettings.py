from typing import Optional

import openai
import requests
from holytools.logging import LoggerFactory
from holytools.configs import PassConfigs, BaseConfigs
from holytools.logging import Loggable

from func_timeout import func_timeout, FunctionTimedOut
# from awsops import AWSRegion
# from awsops.aws_configs import ConfigsAWS

settingsLogger = LoggerFactory.make_logger(name=__name__)

# --------------------------------------------

class LotusSettings(Loggable):
    configs : Optional[BaseConfigs] = None
    enable_validation : bool = False

    @classmethod
    def get(cls, key: str) -> str:
        return cls.configs.get(key)

    @classmethod
    def set_configs(cls, use_local : bool, enable_validation : bool = False):
        if use_local:
            cls.configs = PassConfigs(pass_dirpath='~/Drive/.password-store')
        else:
            raise NotImplementedError
        #     configs = ConfigsAWS(secret_name='lotus_api_keys', region=AWSRegion.EU_NORTH_1.value)

        if enable_validation:
            cls.validation()

        settingsLogger.info(msg=f'Completed setup for all Settings')


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
    def reset(cls):
        cls.configs = None
        cls.enable_validation = False
        settingsLogger.info(msg=f'Reset settings')

    # ----------------------------------------------
    # validation

    @classmethod
    def validation(cls):
        successful_tests = []
        failed_tests = []
        for test in [cls.validate_openai]:
            if not test():
                failed_tests.append(test.__name__)
            else:
                successful_tests.append(test.__name__)

        if failed_tests:
            raise ValueError(f'Validation failed for {failed_tests}')

        settingsLogger.info(msg=f'Successfully performed validations {successful_tests}')

    @classmethod
    def validate_openai(cls) -> bool:
        temp = openai.api_key
        is_successful = False
        err_details = ''
        timeout = 5

        try:
            openai.api_key = cls.get_openai_apikey()
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
                settingsLogger.error(msg=f'Error after test run of openai_api_key: {err_details.__repr__()}')
            openai.api_key = temp
            return is_successful

    @classmethod
    def validate_search_engine(cls) -> bool:
        is_successful = False
        err_details = ''
        try:

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': 'snails',
                'key': cls.get_google_apikey(),
                'cx': cls.get_searchengine_id(),
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
                settingsLogger.error(msg=f'Error after test run of search engine: {err_details}')
            return is_successful


