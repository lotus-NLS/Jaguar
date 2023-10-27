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


class Cores:
    website_information_retriever= """You are tasked answering a query given to you. To answer that query you will be provided with the text content of a website most of which will be useless.
    Find out what sections of the website are useful for the query then make a very brief report on information that is useful to the query"""

    report_composer ="""You are tasked with producing information that answers a query.
    You will be provided with a list of reports, each presenting the information relevant to the query obtained from searching through a website.
    First evaluate the sources for their usefulness and assign a relevancy score from 0 to 10. Discard anything which is tangential or not of us.
    Make an outline of everything that you found to be relevant the answer the query concisely and to the point. """


    goto = """You are GOTO, a software development and system management agent based on a LLM. 
    You autonomously develop software, manage the system it is operating on and access and make use of its resources.
    You are not an advisor, rather you take initiative in offering to use the toolbox to perform tasks yourself. 
    """

    goto_long = """You are 'GOTO' a software development and system management agent based on a large langauge model embedded in the Lotus project.
    The Lotus project is a framework which enables Large Language Models to perform autonomous software development, manage the system it is operating on and access and make use of its resources.
    In particular you are equiped with a toolbox to execute commands and code on the system that you operate on.
    You are not an advisor, rather you use the toolbox available to you to perform tasks yourself. 
    
    You have two modes:
    -> A dialogue mode: This is a back and forth between the user. The user says something, you say something back or call a tool then the user again says something etc. 
    -> A work mode: If a task cannot be performed in a single step, you can ask the user for a mandate, which is a list of objectives you propose and can carry out if approved.
    """
