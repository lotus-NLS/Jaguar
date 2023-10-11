from src.l3_lotus_core.m1_settings_modules import Setting
from src.l3_lotus_core.m1_settings_modules import SettingGrouping, SettingTest


class DialogueSettings(SettingGrouping):
    def __init__(self):
        super().__init__()
        self.enable_introduction : Setting = self.make_setting(label='enable_introduction',
                                                               test=SettingTest.make_empty_test(),
                                                               dtype=bool)

    def check(self):
        pass
