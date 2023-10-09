from __future__ import annotations

from abc import abstractmethod
from typing import Callable

from src.l3_lotus_core.m0_settings._setting import Setting


class SettingGrouping:
    all_settings_in_group = []

    def __init__(self, tests : list[Callable[[],None]]):
        self.tests = tests

    @abstractmethod
    def setup(self):
        pass

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
