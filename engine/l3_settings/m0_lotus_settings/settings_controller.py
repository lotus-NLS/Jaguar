from __future__ import annotations
from typing import Optional
from engine.l3_settings.m1_settings_modules import all_settings

from .CredentialSettings import CredentialSettings
from .DialogueSettings import DialogueSettings


# (10.10.23) D.H. : Settings Terminology
# -> There is a settings resource either locally on the computer or in the cloud
# -> The setup method of the Settings Controller completes only when valid values are obtained for every setting listed
# -> Values are validated by the _tests defined in each SettingsGrouping

# (10.10.23) D.H. : Settings Workflow
# -> If valid values can be retrieved from the settings resource they are loaded up and the setup terminates
# -> If not, the user will be informed for which settings valid values could not be obtained and be asked if he wants to retry
#  via a y/n prompt
# -> If the user does choose to retry he will be asked to enter new values for the settings that failed to validate
# -> When all settings are valid or the user declines to enter new values on the y/n prompt the setup process terminates


# NOTE : Because everything is saved in a single file, setting labels must be unique
# and so must the name of SettingGroupings  also must be unique
# ---------------------------------------------------------


class SettingsController:
    def __init__(self):
        self.credential_settings : CredentialSettings = CredentialSettings()
        self.dialogue_settings : DialogueSettings = DialogueSettings()

    def setup(self, perform_validation = True):


        if perform_validation:
            self.credential_settings.setup()
            self.dialogue_settings.setup()

        else:
            self.credential_settings.pass_all()
            self.dialogue_settings.pass_all()

        print(f'[Debug]: Completed setup for all Settings')


def get_setting(label : str) -> Optional[str]:
    return all_settings.get(label).value
