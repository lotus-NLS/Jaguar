from __future__ import annotations
from typing import Callable

from src.l3_lotus_core.m1_OperatorIO.userIO import user_io
from src.l3_lotus_core.m0_settings._setting import Setting
# ---------------------------------------------------------


class SettingGrouping:

    def __init__(self, tests : list[Callable[[],None]]):
        self.tests : list[callable] = tests
        self.all_settings_in_group : list[Setting] = []

    def make_setting(self, label : str) -> Setting:
        new_setting = Setting(label=label, section=self.__class__.__name__)
        self.all_settings_in_group.append(new_setting)
        return new_setting

    # ---------------------------------------------------------
    # Setup

    def setup(self, is_first_run = True):
        for the_setting in self.get_non_validated_settings():
            the_setting.try_setup_from_file() if is_first_run else the_setting.setup_from_user_input()

        self.test_all()
        valid, non_valid = self.get_validated_settings(), self.get_non_validated_settings()

        for setting in valid:
            setting.save_state_to_file()

        if not len(non_valid) == 0:
            msg = (f'[Error]: {len(non_valid)} setting(s) in {self.__class__.__name__}'
                   f' failed to validate: {[setting.label for setting in non_valid]} Retry setup for those settings? (y/n)')
            if user_io.get_confirmation(msg=msg):
                self.setup(is_first_run=False)


    def get_non_validated_settings(self) -> list[Setting]:
        return [setting for setting in self.all_settings_in_group if not setting.get_is_validated()]


    def get_validated_settings(self) -> list[Setting]:
        return [setting for setting in self.all_settings_in_group if setting.get_is_validated()]


    def test_all(self):
        for test in self.tests:
            try:
                test()
                print(f'[Debug]: Test {test.__name__} completed successfully')
            except Exception as e:
                print(f'[Error]: An error occured while performing test {test.__name__}: {e}')


    def pass_all(self):
        for setting in self.all_settings_in_group:
            setting.validate()

