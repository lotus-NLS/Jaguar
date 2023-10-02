from __future__ import annotations

from typing import Optional, Callable
import openai
import requests

from src.l2_lotus_core.m2_settings.setting_class import all_settings, Setting

# (08.09.23) DH:
# Each Settings group has its own tests that are performed on setup which are used to validate the settings
# It would be impossible to validate each setting on its own since some tests require multiple settings
# At the end of the setup all Credentials must be validated if all tests lotus_run successfully
# If the value for the setting is validated it is saved on the file system in the settings file in the home directory

# NOTE : Setting labels must be unique, CredentialGrouping names also must be unique
# ---------------------------------------------------------


class SettingGrouping:
    all_settings_in_group = []

    def __init__(self, tests : list[Callable[[],None]]):
        self.tests = tests

    def setup(self):
        pass

    @staticmethod
    def get_validated_settings() -> list[Setting]:
        return [setting for setting in Credentials.all_settings_in_group if setting.get_is_validated()]

    @staticmethod
    def get_non_validated_settings() -> list[Setting]:
        return [setting for setting in Credentials.all_settings_in_group if not setting.get_is_validated()]

    @classmethod
    def pass_all(cls):
        for setting in cls.all_settings_in_group:
            setting.validate()

    @staticmethod
    def get_y_or_n(msg : str):
        while True:
            user_input = input(msg)
            if user_input.lower() in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")

        return user_input

    def test_all(self):
        for test in self.tests:
            try:
                test()
                print(f'[Debug]: Test {test.__name__} completed successfully')
            except Exception as e:
                print(f'[Error]: An error occured while performing test {test.__name__}: {e}')


class Credentials(SettingGrouping):
    openai_apikey_label = 'openai_api_key'
    google_apikey_label = 'google_api_key'
    search_engineID_label = 'search_engine_id'

    def __init__(self):
        super(Credentials, self).__init__(tests=[self.openai_apikey_test, self.search_engine_test])
        self.openai_apikey_setting : Setting = self.make_credential_setting(label=Credentials.openai_apikey_label)
        self.google_apikey_setting : Setting = self.make_credential_setting(label=Credentials.google_apikey_label)
        self.search_engineID_setting : Setting = self.make_credential_setting(label=Credentials.search_engineID_label)


    def setup(self, is_first_run = True, is_perform_validation = True) -> None:
        for the_setting in self.get_non_validated_settings():
            the_setting.try_setup_from_file() if is_first_run else the_setting.setup_from_user_input()

        if is_perform_validation:
            self.test_all()
        else:
            self.pass_all()

        for setting in self.get_validated_settings():
            setting.save_state_to_file()

        non_validated_settings = self.get_non_validated_settings()
        count_non_validated_settings = len(non_validated_settings)
        if not count_non_validated_settings == 0:
            msg = f'[Error]: {count_non_validated_settings} setting(s) failed to validate. Retry setup for those settings? (y/n) \n'
            if self.get_y_or_n(msg) == 'y':
                self.setup(is_first_run=False)


    @staticmethod
    def make_credential_setting(label : str) -> Setting:
        new_setting = Setting(label=label, section=Credentials.__name__)
        Credentials.all_settings_in_group.append(new_setting)
        return new_setting


    def openai_apikey_test(self) -> None:
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


class SettingsController:
    def __init__(self):
        self.credential_settings = Credentials()

    # TODO 0.4: Instead of listing each of the settings group can introduce some mechanism to
    # introduce every instance of SettingsGroup to some list and then iterate through that, could also save the init listings
    def setup(self, perform_validation = True):
        self.credential_settings.setup(is_perform_validation=perform_validation)
        print(f'[Debug]: Completed setup for all Settings')


def get_setting(label : str) -> Optional[str]:
    return all_settings.get(label).value
