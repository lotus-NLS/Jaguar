from __future__ import annotations
from typing import Callable

from src.l3_lotus_core.m2_OperatorIO.userIO import user_io
from src.l3_lotus_core.m1_settings_modules._setting import Setting
# ---------------------------------------------------------

class SettingTest:
    @classmethod
    def make_empty_test(cls):
        def empty_test() -> bool:
            return True

        return cls(test_body=empty_test)

    def __init__(self, test_body : Callable[[],bool]):
        self.test_body : Callable[[],bool] = test_body
        self.checked_settings : list[Setting] = []

    def add_checked_setting(self, the_setting : Setting):
        self.checked_settings.append(the_setting)

    def check_setting_validity(self):
        is_successful = self.test_body()
        if is_successful:
            for setting in self.checked_settings:
                setting.validate_functionality()



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
        # Type checks
        for setting in self.all_settings_in_group:
            setting.test_type_conformity()

        # Validity checks
        for test in self.tests:
            tested_labels_settings = [setting.label for setting in test.checked_settings]
            try:
                test.check_setting_validity()
                print(f'[Debug]: Functionality test {test.test_body.__name__} for settings {tested_labels_settings} completed successfully')
            except Exception:
                print(f'[Error]: An error occured while performing test {test.__name__} or settings {tested_labels_settings}')


    def pass_all(self):
        for setting in self.all_settings_in_group:
            setting.validate_functionality()

