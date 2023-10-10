from __future__ import annotations
from typing import Callable

from src.l3_lotus_core.m1_OperatorIO.userIO import user_io
from src.l3_lotus_core.m0_settings._setting import Setting
# ---------------------------------------------------------


class SettingGrouping:
    all_settings_in_group = []

    def __init__(self, tests : list[Callable[[],None]]):
        self.tests = tests


    def setup(self, is_first_run = True, is_perform_validation = True):
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
            msg = f'[Error]: {count_non_validated_settings} setting(s) failed to validate. Retry setup for those settings? (y/n)'
            if user_io.get_confirmation(msg=msg):
                self.setup(is_first_run=False)


    @classmethod
    def get_validated_settings(cls) -> list[Setting]:
        return [setting for setting in cls.all_settings_in_group if setting.get_is_validated()]


    @classmethod
    def get_non_validated_settings(cls) -> list[Setting]:
        return [setting for setting in cls.all_settings_in_group if not setting.get_is_validated()]


    @classmethod
    def pass_all(cls):
        for setting in cls.all_settings_in_group:
            setting.validate()


    @classmethod
    def make_setting(cls, label : str) -> Setting:
        new_setting = Setting(label=label, section=cls.__name__)
        cls.all_settings_in_group.append(new_setting)
        return new_setting


    def test_all(self):
        for test in self.tests:
            try:
                test()
                print(f'[Debug]: Test {test.__name__} completed successfully')
            except Exception as e:
                print(f'[Error]: An error occured while performing test {test.__name__}: {e}')
