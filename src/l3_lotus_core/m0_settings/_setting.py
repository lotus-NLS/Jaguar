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
    def __init__(self, label : str, section : str, dtype : type):
        self.label : str = label
        self.section : str = section
        self.value : Union[None, str] = None
        self.dtype : type = dtype

        self._is_type_conform : bool = False
        self._is_functional : bool = False

        all_settings[self.label] = self

    def get_is_validated(self) -> bool:
        return self._is_functional and self._is_type_conform

    # --------------------------------------------
    # Setup value

    def setup_from_file(self):
        config_parser.read(config_path)
        self.value = config_parser.get(self.section, self.label)


    def setup_from_user_input(self):
        self.value = user_io.get_user_msg(f'Enter value for setting {self.label}')


    def test_type_conformity(self):
        self._is_type_conform = isinstance(self.value, self.dtype)


    def validate_functionality(self):
        self._is_functional = True


    def save_state_to_file(self):
        try:
            if self.section not in config_parser.sections():
                config_parser.add_section(self.section)
            config_parser.set(section=self.section, option=self.label, value=self.value)
            with open(config_path, 'w') as f:
                config_parser.write(f)
            print(f'[Debug]: Saved value for setting {self.label} to settings file')

        except Exception as e:
            print(f'[Error]: An exception occured while trying to save setting {self.label}: {e}')
