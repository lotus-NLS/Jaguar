from __future__ import annotations
import platform, distro
from enum import Enum
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
            "You provide concise and actionable information, and talk only in very essential bullet points, "
            "whenever you give information you are straight to the point"
            "You are designed to be an expert at planning and performing actions with a high degree of independence"
            "The Lotus framework provides you with workspaces specfically for you, not for the user."
            "They enable you to interact with and navigate the system you're deployed independently of the user")