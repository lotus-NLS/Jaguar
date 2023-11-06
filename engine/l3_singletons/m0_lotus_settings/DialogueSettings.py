from engine.l3_singletons.m1_settings_modules import Setting
from engine.l3_singletons.m1_settings_modules import SettingGrouping, SettingTest


class DialogueSettings(SettingGrouping):
    def __init__(self):
        super().__init__()
        self.enable_introduction : Setting = self.make_setting(label='enable_introduction',
                                                               test=SettingTest.make_automatic_pass(),
                                                               dtype=bool)
    def get_enable_introduction(self) -> bool:
        return self.enable_introduction.value

    def check(self):
        pass
