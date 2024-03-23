from __future__ import annotations
import platform, distro
from enum import Enum
from engine.l2_os import LotusText
# ----------------------------------------------------


class Identity:
    def __init__(self, core : Core):
        self.core : Core = core
        self.os_information : str = self.get_detailed_os_info()

    @classmethod
    def GOTO(cls):
        return cls(core=Core.GOTO)

    def get_str(self) -> str:
        msg = f'{self.core.value}\n'
        msg += f'You operate on the OS: {self.os_information}'
        return msg


    @staticmethod
    def get_detailed_os_info():
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
    GOTO = ("You are 'GOTO' a software development and system management agent based on a LLM,"
            "embedded in the Lotus framework."
            "You develop software, manage files and other resoucres and setup development environments"
            " including installation of packages, tools and libraries")

# mode_msg = ('I am currently in work mode and cannot speak to the user.'
#             'The root objective must be completed or canceled via UPDATE_MANDATE to get back to dialogue mode and converse with the user.'
#             'Once an objective is completed, I will mark it as complete using UPDATE_MANDATE')


