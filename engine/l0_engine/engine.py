import time

from api import Entry
from engine.l1_agents import Agent, StepInfo
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, Terminal
from holytools.logging import Loggable
from .dev_monitor import MonitorServer
from .settings import LotusCredentials
from ..l1_agents.protocol.stepinfo import Workflowy


# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        self.creds = LotusCredentials()
        model = OpenAIModel.default_model(api_key=self.creds.get_openai_apikey())
        aos = AOS(workspaces=[Terminal()])
        self.agent: Agent = Agent(model=model, aos=aos)
        self.dev_monitor : MonitorServer = MonitorServer(agent=self.agent)
        self.is_alive : bool = True

    # ---------------------------------------------
    # routines

    def user_routine(self):
        self._launch()
        while self.is_alive:
            if self.agent.is_working():
                self._work_step()
            else:
                self._converse_step()

        self._stop()

    def query_routine(self, workflowy : Workflowy, query : str, max_steps : int) -> str:
        self.agent.workflowy = workflowy
        num_steps = 0
        while self.agent.is_working() and num_steps < max_steps:
            self._work_step()
            num_steps += 1
        task = StepInfo(memory=Entry.user(msg=query))
        response = self.agent.handle(task=task)
        answer = ''
        for text in response.get_text_stream():
            answer += text
        return answer

    # ---------------------------------------------
    # subroutines

    def _launch(self):
        self.log(f'Lotus started')
        self.dev_monitor.serve()

    def _work_step(self):
        work_task = StepInfo(notice=Entry.agent(msg=f'My current todo list:\n'
                                                    f'{self.agent.workflowy.root.get_tree()}'))
        self.agent.handle(task=work_task)

    def _converse_step(self):
        user_input = input(f'\nUser: ')
        if user_input == 'exit':
            self.is_alive = False
            return

        task = StepInfo(memory=Entry.user(msg=user_input))
        response = self.agent.handle(task=task)
        for text in response.get_text_stream():
            print(text, end='', flush=True)
            time.sleep(0.05)

    def _stop(self):
        self.log(f'Lotus stopped')
        self.dev_monitor.kill()


