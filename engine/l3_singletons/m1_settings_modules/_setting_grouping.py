from __future__ import annotations
from typing import Callable
from engine.l3_singletons.m0_server import EngineIO

from ._setting import Setting

# ---------------------------------------------------------

class SettingTest:
    @classmethod
    def make_empty_test(cls):
        def empty_test() -> bool:
            return True

        return cls(test_body=empty_test)

    def __init__(self, test_body : Callable[[],bool]):
        self.do_check : Callable[[],bool] = test_body
        self.checked_settings : list[Setting] = []

    def add_checked_setting(self, the_setting : Setting):
        self.checked_settings.append(the_setting)

    def check_setting_validity(self) -> bool:
        is_successful = self.do_check()
        if is_successful:
            for setting in self.checked_settings:
                setting.validate_functionality()
        return is_successful



class SettingGrouping:
    def __init__(self,):
        self.tests : set[SettingTest] = set()
        self.all_settings_in_group : list[Setting] = []


    def make_setting(self, label : str, test : SettingTest, dtype : type = str) -> Setting:
        new_setting = Setting(label=label, section=self.__class__.__name__, dtype = dtype)

        self.all_settings_in_group.append(new_setting)
        test.add_checked_setting(the_setting=new_setting)
        self.tests.add(test)

        return new_setting

    # ---------------------------------------------------------
    # Value setup

    def setup(self, is_first_run = True):
        for the_setting in self.get_non_validated_settings():
            the_setting.set_value(from_file = is_first_run)

        self.perform_tests()
        valid, non_valid = self.get_validated_settings(), self.get_non_validated_settings()

        for setting in valid:
            setting.save_state_to_file()

        if not len(non_valid) == 0:
            msg = (f'[Error]: {len(non_valid)} setting(s) in {self.__class__.__name__}'
                   f' failed to validate: {[setting.label for setting in non_valid]}\nRetry setup for those settings? (y/n)')

            EngineIO().post_engine_message(msg=msg)

            if EngineIO().get_confirmation():
                self.setup(is_first_run=False)


    def get_non_validated_settings(self) -> list[Setting]:
        return [setting for setting in self.all_settings_in_group if not setting.get_is_validated()]


    def get_validated_settings(self) -> list[Setting]:
        return [setting for setting in self.all_settings_in_group if setting.get_is_validated()]


    def perform_tests(self):
        for test in self.tests:
            tested_labels_settings = [setting.label for setting in test.checked_settings]
            if test.check_setting_validity():
                print(f'[Debug]: Functionality test {test.do_check.__name__} for settings {tested_labels_settings} completed successfully')
            else:
                print(f'[Error]: Functionality test {test.do_check.__name__} failed. Check settings {tested_labels_settings}')


    def pass_all(self):
        for setting in self.all_settings_in_group:
            setting.validate_functionality()

