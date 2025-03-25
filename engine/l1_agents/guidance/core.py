from __future__ import annotations

import platform, distro
from enum import Enum
from datetime import datetime
from engine.l2_models.language import Entry


# ----------------------------------------------------


class Core:
    def __init__(self, identity : Identity):
        self.identity : Identity = identity
        self.os_information : str = self.get_os_info()

    @classmethod
    def GOTO(cls):
        return cls(identity=Identity.GOTO)

    def as_system_entry(self) -> Entry:
        return Entry.system(msg=self.as_str())

    def as_str(self) -> str:
        msg = f'{self.identity.value}\n'
        msg += f'You operate on the OS: {self.os_information}. '
        msg += f'The current date is {self.get_date()} and the current time in this moment is {self.get_time()}.'
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

    @staticmethod
    def get_date() -> str:
        current_dt = datetime.now()
        date = current_dt.date()
        return date.strftime('%d.%m.%Y')

    @staticmethod
    def get_time() -> str:
        current_dt = datetime.now()
        time = current_dt.time()
        return time.strftime('%H:%M:%S')


class Identity(Enum):
    GOTO = ("You are 'GOTO' a software development and system management agent."
            "You can operate either in conversation mode or in work mode which decouples you from the user"
            "and allows you to freely perform tasks and take as many steps as you need to work on your current objectives."
            "While you are very accurate usually, when publicly available data you used as training material is sparse you"
            " may accidentially and unknowingly confidently produce code or give information that is actually just guesswork."
            "Whenever variables, methods and classes in your code are unresolved consider if accidential guesswork is at play.")
