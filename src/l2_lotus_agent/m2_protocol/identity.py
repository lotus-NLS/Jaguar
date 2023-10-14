from __future__ import annotations
import platform, distro

# ----------------------------------------------------


class Identity:
    def __init__(self,core : str):
        self.core : str = core
        self.os_information : str = self.get_detailed_os_info()


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

    def get_str(self) -> str:
        identity_msg = f'{self.core}\n'
        os_msg = f'You operate on the OS: {self.os_information}'

        return identity_msg+os_msg



