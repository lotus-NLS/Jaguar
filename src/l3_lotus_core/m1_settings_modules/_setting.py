from __future__ import annotations
import ast
import configparser
import os
from typing import Union, Optional


from src.l3_lotus_core.m2_OperatorIO.userIO import user_io
from src.l3_lotus_core.m2_OperatorIO.dev_logger import get_exception_msg

# ----------------------------------------------------

home = os.path.expanduser("~")
config_path = os.path.join(home, 'settings_[uuid_4d9498a7-2f46-4372-9c49-c96e3c41d4f7].ini')
config_parser = configparser.ConfigParser()
all_settings = {}


class Setting:
    def __init__(self, label : str, section : str, dtype : type):
        self.label : str = label
        self.section : str = section
        self.dtype : type = dtype
        self.value: Union[None,dtype] = None

        self._is_functional : bool = False

        all_settings[self.label] = self


    def get_is_validated(self) -> bool:
        return self._is_functional and not self.value is None

    # --------------------------------------------
    # Setup value

    def set_value(self,from_file : bool):
        value_str = ''
        _ = value_str

        if from_file:
            try:
                config_parser.read(config_path)
                value_str = config_parser.get(self.section, self.label)
            except:
                print(get_exception_msg(text='An error occured while trying to read value from file'))
                return

        else:
            msg = f'Enter value for setting {self.label} (Type: {self.dtype.__name__}'
            msg += ', Options: True/False)' if self.dtype is bool else ')'
            value_str = user_io.get_user_msg(msg)

        self.value = self.get_typecast_value(value_str=value_str)


    def get_typecast_value(self, value_str : str) -> Optional[object]:
        if self.dtype is str:
            return value_str

        value = None
        try:
            eval_value = ast.literal_eval(value_str)
            cast_value = self.dtype(eval_value)

            if eval_value == cast_value:
                value = cast_value

        finally:
            return value


    def validate_functionality(self):
        self._is_functional = True


    def save_state_to_file(self):
        try:
            if self.section not in config_parser.sections():
                config_parser.add_section(self.section)
            config_parser.set(section=self.section, option=self.label, value=str(self.value))
            with open(config_path, 'w') as f:
                config_parser.write(f)
            print(f'[Debug]: Saved value for setting {self.label} to settings file')

        except Exception as e:
            print(f'[Error]: An exception occured while trying to save setting {self.label}: {e}')
