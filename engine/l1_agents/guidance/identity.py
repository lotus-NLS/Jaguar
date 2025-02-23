from __future__ import annotations
import platform, distro
from enum import Enum

from engine.l2_models.language import Entry


# ----------------------------------------------------


class Identity:
    def __init__(self, core : Core):
        self.core : Core = core
        self.os_information : str = self.get_os_info()

    @classmethod
    def GOTO(cls):
        return cls(core=Core.GOTO)

    def as_system_entry(self) -> Entry:
        return Entry.system(msg=self.as_str())

    def as_str(self) -> str:
        msg = f'{self.core.value}\n'
        msg += f'You operate on the OS: {self.os_information}'
        return msg

    @staticmethod
    def get_os_info():
        system = f'{platform.system()}'
        detail = system

        try:
            if system == "Windows":
                detail += f" version {platform.release()}"
            elif system == "Darwin":
                mac_ver, _, _ = platform.mac_ver()
                detail += f" version {mac_ver}"
            elif system == "Linux":
                distro_name, distro_version = distro.id(), distro.version()
                detail += f" - {distro_name} version {distro_version}"
        except Exception as e:
            detail += f" (Error obtaining additional details: {e})"

        return detail


class Core(Enum):
    GOTO = ("You are 'GOTO' a software development and system management agent."
            "You can operate either in conversation mode or in work mode which decouples you from the user"
            "and allows you to freely perform tasks and take as many steps as you need to work on your current objectives."
            "Execute one tool at a time.")