import time

from api import Entry
from engine.l1_agents import Agent, StepInfo
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, TextEditor, Terminal, FileExplorer, Browser
from holytools.logging import Loggable
from .dev_monitor import MonitorServer
from .settings import LotusCredentials

# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self, use_local_credentials : bool = True):
        super().__init__()
        self.creds = LotusCredentials(use_local=use_local_credentials)
        self.agent: Agent = Agent(model=self.get_model(), aos=self.get_aos())
        self.dev_monitor : MonitorServer = MonitorServer(agent=self.agent)
        self.is_alive : bool = True

    def get_model(self):
        return OpenAIModel.default_model(api_key=self.creds.get_openai_apikey())

    def get_aos(self):
        browser = Browser(google_api_key=self.creds.get_google_apikey(), searchengine_id=self.creds.get_searchengine_id())
        return AOS(workspaces=[TextEditor(), Terminal(), FileExplorer(), browser])

    # ---------------------------------------------

    def run(self):
        self._launch()
        while self.is_alive:
            if self.agent.is_working():
                self.work_step()
            else:
                self.converse_step()

        self.stop()

    def work_step(self):
        work_task = StepInfo(notice=Entry.agent(msg=f'My current todo list:\n'
                                                    f'{self.agent.workflowy.root_objective.get_tree()}'))
        self.agent.handle(task=work_task)


    def converse_step(self):
        user_input = input(f'\nUser: ')
        if user_input == 'exit':
            self.is_alive = False

        task = StepInfo(memory=Entry.user(msg=user_input))
        response = self.agent.handle(task=task)
        for text in response.get_text_stream():
            print(text, end='', flush=True)
            time.sleep(0.05)


    def request_terminal(self):
        self._launch()
        task = StepInfo(memory=Entry.user(msg='Open terminal in /home/daniel'))
        response = self.agent.handle(task=task)
        for text in response.get_text_stream():
            print(text)

    def _launch(self):
        self.log(f'Lotus started')
        self.dev_monitor.run()
        time.sleep(1)

    def stop(self):
        self.log(f'Lotus stopped')
        self.dev_monitor.kill()


