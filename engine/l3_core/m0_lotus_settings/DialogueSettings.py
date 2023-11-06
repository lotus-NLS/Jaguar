from engine.l3_core.m1_settings_modules import Setting
from engine.l3_core.m1_settings_modules import SettingGrouping, SettingTest


class DialogueSettings(SettingGrouping):
    enable_introduction_label = 'enable_introduction'

    def __init__(self):
        super().__init__()
        self.enable_introduction : Setting = self.make_setting(label=DialogueSettings.enable_introduction_label,
                                                               test=SettingTest.make_empty_test(),
                                                               dtype=bool)

    def check(self):
        pass
