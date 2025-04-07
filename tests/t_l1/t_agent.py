from engine.l0_main.lotus_io import LotusIO
from engine.l1_agents import Agent
from engine.l2_models import OpenAIModel, InfConfig
from engine.l3_aos import Browser, Terminal, AOS
from engine.l3_aos.tools import ToolOutput
from tests.credtest import CredTest
from tests.t_l2.base import Greet

from scenarios.taskprovider import TaskProvider

# ------------------------------------------

class TestAgent(CredTest):
    def setUp(self):
        browser = Browser(google_api_key=self.credentials.google_api_key,
                          searchengine_id=self.credentials.search_engine_id)
        terminal = Terminal()
        aos = AOS(workspaces=[terminal, browser])
        model = OpenAIModel.default_model(api_key=self.credentials.openai_api_key)
        self.agent = Agent(aos=aos, model=model)
        self.default_inf_config : InfConfig = InfConfig()
        self.task_provider : TaskProvider = TaskProvider()
        self.lotusIO : LotusIO = LotusIO(disable_socket=True)

    def test_memory_context(self):
        content = f'Hello there!'
        step = self.agent.talk(msg=content)
        view = step.post_ctx.get_view()

        print(f'- View of context\n{view}')
        self.assertTrue(content in view)

    def test_tasktracker_context(self):
        test_task = self.task_provider.get_task(name='test')
        last_step = None
        work_notice = self.agent.task_tracker.work_notice

        for j, step in enumerate(self.agent.work(test_task, max_steps=2)):
            last_step = step
            if j == 0:
                ctx_view = step.post_ctx.get_view()

                self.assertTrue('TaskTracker[Active]' in ctx_view)
                self.assertTrue(work_notice in ctx_view)


        self.assertTrue('TaskTracker[Archived]' in last_step.post_ctx.get_view())
        self.assertTrue('TaskTracker[Active]' not in last_step.post_ctx.get_view())

    # Measure tool docs there
    # Measure
    def test_aos_context(self):
        pass

    # Test cases for is_working:
        # All complete -> Not working
        # Subtaks complete -> Not working
        # Task tracker closed -> Not working
        # Not all complete -> Working
    def test_is_working(self):
        pass


    def test_required_tool_use(self):
        greet_tool = Greet()
        inf_config = InfConfig(required_tool=greet_tool)
        step = self.agent.handle(inf_config=inf_config)

        outputs : list[ToolOutput] = step.tool_outputs

        self.assertTrue(len(outputs) == 1)
        self.assertTrue(outputs[0].tool_name == greet_tool.get_name())


    def test_freeze_ws(self):
        self.agent.task_tracker.open_action.execute({})
        self.agent.task_tracker.close_action.execute({})

        context = self.agent.get_context(inf_config=InfConfig())
        context_view = context.get_view()
        print(f'- View of context\n{context_view}')

        self.assertTrue(f'## [Closed workspace] ##' in context_view)


if __name__ == "__main__":
    TestAgent.execute_all()