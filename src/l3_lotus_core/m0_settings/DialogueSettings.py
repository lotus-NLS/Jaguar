from src.l3_lotus_core.m0_settings._setting import Setting
from src.l3_lotus_core.m0_settings._setting_grouping import SettingGrouping, SettingTest


class DialogueSettings(SettingGrouping):
    def __init__(self):
        super().__init__()
        self.enable_introduction : Setting = self.make_setting(label='enable_introduction',
                                                               test=SettingTest.make_empty_test())

    def check(self):
        pass
