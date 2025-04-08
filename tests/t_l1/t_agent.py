import time

from engine.l0_main.lotus_io import LotusIO
from engine.l1_agents import Agent, Task, TaskTracker
from engine.l2_models import OpenAIModel, InfConfig
from engine.l3_aos import Browser, Terminal, AOS
from engine.l3_aos.tools import ToolOutput
from engine.l3_aos.workspaces.python_ide import PythonIDE
from eval.task.resources.taskprovider import TaskProvider
from tests.basetests import CredTest
from tests.t_l2.base import Greet


# ------------------------------------------

class TestAgent(CredTest):
    def setUp(self):
        browser = Browser(google_api_key=self.credentials.google_api_key,
                          searchengine_id=self.credentials.search_engine_id)
        terminal = Terminal()
        ide = PythonIDE()
        aos = AOS(workspaces=[terminal, browser, ide])
        model = OpenAIModel.default_model(api_key=self.credentials.openai_api_key)
        self.agent: Agent = Agent(aos=aos, model=model)
        self.default_inf_config: InfConfig = InfConfig()
        self.task_provider: TaskProvider = TaskProvider()
        self.lotusIO: LotusIO = LotusIO(disable_socket=True)

    def test_memory_context(self):
        content = f'Hello there!'
        step = self.agent.talk(msg=content)
        view = step.post_ctx.get_view()

        print(f'- View of context\n{view}')
        self.assertTrue(content in view)


    def test_aos_context(self):
        ctx = self.agent.get_context(inf_config=self.default_inf_config)

        total_view = ''
        for d in ctx.docs:
            view = d.get_view()
            total_view += f'{view}\n'
        print(f'-> Total tool doc view:\n{total_view}')

        self.assertTrue(f'{PythonIDE.__name__}_open' in total_view)
        self.assertTrue(f'{Terminal.__name__}_open' in total_view)
        self.assertTrue(f'{Browser.__name__}_open' in total_view)
        self.assertTrue(not f'{TaskTracker.__name__}_open' in total_view)



    #
    # # Test cases for is_working:
    #     # All complete -> Not working
    #     # Subtaks complete -> Not working
    #     # Task tracker closed -> Not working
    #     # Not all complete -> Working
    # def test_is_working(self):
    #     pass
    #
    # def test_headlines(self):
    #     pass

    def test_required_tool_use(self):
        greet_tool = Greet()
        inf_config = InfConfig(required_tool=greet_tool)
        step = self.agent.handle(inf_config=inf_config)

        outputs: list[ToolOutput] = step.tool_outputs

        self.assertTrue(len(outputs) == 1)
        self.assertTrue(outputs[0].tool_name == greet_tool.get_name())

    def test_tasktracker_freeze(self):
        task = Task.from_yaml(s='- Complete this task')
        work_notice = self.agent.task_tracker.work_notice
        close_tool = self.agent.task_tracker.close_action

        close_step = None
        for _ in self.agent.work(task=task, max_steps=1):
            close_step = self.agent.handle(inf_config=InfConfig.single_tool(close_tool))

        gen_ctx_view = close_step.pre_ctx.get_view()
        self.assertTrue('TaskTracker[Active]' in gen_ctx_view)
        self.assertTrue(work_notice in gen_ctx_view)

        post_ctx_view = close_step.post_ctx.get_view()
        self.assertTrue('TaskTracker[Archived]' in post_ctx_view)
        self.assertTrue('TaskTracker[Active]' not in post_ctx_view)
        self.assertTrue(work_notice not in post_ctx_view)


if __name__ == "__main__":
    ta = TestAgent()
    ta.execute_all()
