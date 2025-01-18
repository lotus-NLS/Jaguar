import time

from api import Entry
from engine.l1_agents import Agent, StepInfo, Workflowy
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, Terminal
from holytools.logging import Loggable
from .dev_monitor import MonitorServer
from .settings import LotusCredentials



# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        self._creds = LotusCredentials()
        model = OpenAIModel.default_model(api_key=self._creds.get_openai_apikey())
        aos = AOS(workspaces=[Terminal()])
        self._agent: Agent = Agent(model=model, aos=aos)
        self._dev_monitor : MonitorServer = MonitorServer(agent=self._agent)
        self._is_alive : bool = True
        self._launch()

    # ---------------------------------------------
    # routines

    def user_routine(self):
        while self._is_alive:
            if self._agent.is_working():
                self._work_step()
            else:
                self._converse_step()

    def resarch_routine(self, workflowy : Workflowy, query : str, max_steps : int) -> str:
        self._agent.workflowy = workflowy

        num_steps = 0
        while self._agent.is_working() and num_steps < max_steps:
            self._work_step()
            num_steps += 1
        task = StepInfo(memory=Entry.user(msg=query))
        response = self._agent.handle(task=task)
        answer = ''
        for text in response.get_text_stream():
            answer += text
        print(f'The following answer was provided: {answer}')

        return answer

    # ---------------------------------------------
    # subroutines

    def _launch(self):
        self.log(f'Lotus started')
        self._dev_monitor.serve()

    def _work_step(self):
        work_task = StepInfo(notice=Entry.agent(msg=f'My current todo list:\n'
                                                    f'{self._agent.workflowy.root.get_tree()}'))
        self._agent.handle(task=work_task)

    def _converse_step(self):
        user_input = input(f'\nUser: ')
        if user_input == 'exit':
            self._is_alive = False
            return

        task = StepInfo(memory=Entry.user(msg=user_input))
        response = self._agent.handle(task=task)
        for text in response.get_text_stream():
            print(text, end='', flush=True)
            time.sleep(0.05)

    def _stop(self):
        self.log(f'Lotus stopped')
        self._dev_monitor.kill()


