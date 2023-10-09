from src.l3_lotus_core.m0_settings.setting import SettingGrouping, Setting


class DialogueSettings(SettingGrouping):
    def __init__(self):
        super().__init__(tests= [])
        self.enable_introduction : Setting = self.make_dialogue_setting(label='enable_introduction')


    def setup(self):
        self.pass_all()

    @staticmethod
    def make_dialogue_setting(label : str) -> Setting:
        new_setting = Setting(label=label, section=DialogueSettings.__name__)
        DialogueSettings.all_settings_in_group.append(new_setting)
        return new_setting
