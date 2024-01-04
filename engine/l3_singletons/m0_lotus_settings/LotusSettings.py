import logging

from .CredentialSettings import CredentialSettings
from .DialogueSettings import DialogueSettings

class LotusSettings:
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

        logging.info(f'Completed setup for all Settings')
