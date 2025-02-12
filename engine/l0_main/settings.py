import openai
import requests
from func_timeout import func_timeout, FunctionTimedOut

from holytools.configs import FileConfigs
from holytools.logging import Loggable

# --------------------------------------------

class LotusCredentials(Loggable):
    def __init__(self, enable_validation : bool = False):
        super().__init__()
        self.configs = FileConfigs.credentials()
        if enable_validation:
            self.perform_validation()
        self.info(msg=f'Completed setup for all Settings')

    def get_openai_apikey(self) -> str:
        return self._get('openai_api_key')

    def get_google_apikey(self) -> str:
        return self._get('google_api_key')

    def get_searchengine_id(self) -> str:
        return self._get('search_engine_id')

    def _get(self, key: str) -> str:
        return self.configs.get(key)

    # ----------------------------------------------
    # validation

    def perform_validation(self):
        successful_tests = []
        failed_tests = []
        for test in [self.validate_openai, self.validate_search_engine]:
            if not test():
                failed_tests.append(test.__name__)
            else:
                successful_tests.append(test.__name__)

        if failed_tests:
            raise ValueError(f'Validation failed for {failed_tests}')

        self.info(msg=f'Successfully performed validations {successful_tests}')

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
                self.error(msg=f'Error after test run of openai_api_key: {err_details.__repr__()}')
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
                self.error(msg=f'Error after test run of search engine: {err_details}')
            return is_successful


