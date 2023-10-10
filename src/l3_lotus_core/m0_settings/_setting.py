from __future__ import annotations

import configparser
import os
from typing import Union


from src.l3_lotus_core.m1_OperatorIO.userIO import user_io

# ----------------------------------------------------

home = os.path.expanduser("~")
config_path = os.path.join(home, 'settings_[uuid_4d9498a7-2f46-4372-9c49-c96e3c41d4f7].ini')
config_parser = configparser.ConfigParser()
all_settings = {}


class Setting:
    def __init__(self,label : str, section : str):
        self.label : str = label
        self.section : str = section
        self.value : Union[None, str] = None
        self._is_validated : bool = False

        all_settings[self.label] = self

    # --------------------------------------------
    # Setup

    def validate(self):
        self._is_validated = True

    def save_state_to_file(self):
        try:
            if self.section not in config_parser.sections():
                config_parser.add_section(self.section)
            config_parser.set(section=self.section,option=self.label,value=self.value)
            with open(config_path,'w') as f:
                config_parser.write(f)
            print(f'[Debug]: Saved value for setting {self.label} to settings file')

        except Exception as e:
            print(f'[Error]: An exception occured while trying to save setting {self.label}: {e}')


    def try_setup_from_file(self):
        try:
            self.set_value(is_from_file=True)
        except Exception as e:
            print(
                f'[Error]: An error occured while trying to obtain valid setting value for setting {self.label} from settings file: {e}')
            self.set_value(is_from_file=False)

    def setup_from_user_input(self):
        self.set_value(is_from_file=False)

    # --------------------------------------------
    # get

    def get_is_validated(self) -> bool:
        return self._is_validated

    def set_value(self, is_from_file : bool):
        if is_from_file:
            config_parser.read(config_path)
            self.value = config_parser.get(self.section, self.label)

        else:
            self.value = user_io.get_user_msg(f'Enter value for setting {self.label}')


