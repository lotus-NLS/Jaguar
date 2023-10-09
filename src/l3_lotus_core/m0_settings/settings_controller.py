from __future__ import annotations

from typing import Optional

from src.l3_lotus_core.m0_settings.CredentialSettings import CredentialSettings
from src.l3_lotus_core.m0_settings._setting import all_settings
from src.l3_lotus_core.m0_settings.DialogueSettings import DialogueSettings


# (08.09.23) DH:


# Each Settings group has its own tests that are performed on setup which are used to validate the settings
# It would be impossible to validate each setting on its own since some tests require multiple settings
# At the end of the setup all Credentials must be validated if all tests lotus_run successfully
# If the value for the setting is validated it is saved on the file system in the settings file in the home directory

# NOTE : Setting labels must be unique, CredentialGrouping names also must be unique
# ---------------------------------------------------------


class SettingsController:
    def __init__(self):
        self.credential_settings : CredentialSettings = CredentialSettings()
        self.dialogue_settings : DialogueSettings = DialogueSettings()

    def setup(self, perform_validation = True):
        self.credential_settings.setup(is_perform_validation=perform_validation)
        self.dialogue_settings.setup()
        print(f'[Debug]: Completed setup for all Settings')


def get_setting(label : str) -> Optional[str]:
    return all_settings.get(label).value
