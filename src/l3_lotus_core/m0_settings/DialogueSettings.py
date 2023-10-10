from src.l3_lotus_core.m0_settings._setting import Setting
from src.l3_lotus_core.m0_settings._setting_grouping import SettingGrouping


class DialogueSettings(SettingGrouping):
    def __init__(self):
        # super().__init__(tests= [self.no])
        super().__init__(tests= [])
        self.enable_introduction : Setting = self.make_setting(label='enable_introduction')

    # def no(self):
    #     pass
