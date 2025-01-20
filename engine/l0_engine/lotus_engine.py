import time

from engine.l1_agents import Agent, Step
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, Terminal
from engine.l3_aos.workspaces.workflowy import Workflowy
from holytools.logging import Loggable
from .settings import LotusCredentials
from ..l2_models.context import Entry

# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        self._creds = LotusCredentials()
        self._is_alive : bool = True

    def user_routine(self):
        agent = self._get_default_agent(aos=self._get_default_aos())
        while self._is_alive:
            if agent.is_working():
                self._work_step(agent=agent)
            else:
                self._converse_step(agent=agent)

    def resarch_routine(self, workflowy : Workflowy, query : str, max_steps : int) -> str:
        aos = AOS(workspaces=[Terminal()], workflowy=workflowy)
        agent = self._get_default_agent(aos=aos)

        num_steps = 0
        while agent.is_working() and num_steps < max_steps:
            self._work_step(agent)
            num_steps += 1
        task = Step(memory=Entry.user(msg=query))
        response = agent.handle(step=task)
        answer = ''
        for text in response.get_text_stream():
            answer += text
        print(f'The following answer was provided: {answer}')

        return answer

    @staticmethod
    def _get_default_aos() -> AOS:
        return AOS(workspaces=[Terminal()])

    def _get_default_agent(self, aos : AOS):
        model = OpenAIModel.default_model(api_key=self._creds.get_openai_apikey())
        return Agent(model=model, aos=aos)

    # ---------------------------------------------
    # steps

    @staticmethod
    def _work_step(agent : Agent):
        work_task = Step(notice=Entry.agent(msg=f'My current todo list:\n'
                                                    f'{agent.aos.workflowy.root.get_tree()}'))
        agent.handle(step=work_task)

    def _converse_step(self, agent : Agent):
        user_input = input(f'\nUser: ')
        if user_input == 'exit':
            self._is_alive = False
            return

        task = Step(memory=Entry.user(msg=user_input))
        response = agent.handle(step=task)
        for text in response.get_text_stream():
            print(text, end='', flush=True)
            time.sleep(0.05)


