from engine.l1_agents import Agent
from engine.l1_agents.tasks import Task, TaskTracker
from engine.l2_models import InfConfig, Step
from engine.l3_aos import Browser, Terminal, AOS
from engine.l3_aos.tools import ToolOutput
from engine.l3_aos.workspaces.python_ide import PythonIDE
from tests.basetests import AgentTest
from tests.t_l2.base import Greet

# ------------------------------------------

class TestAgent(AgentTest):
    def setUp(self):
        super().setUp()
        self.mock_agent = MockAgent(model=self.model, aos=AOS.empty())


    def test_memory_context(self):
        content = f'Hello there!'
        step = self.mock_agent.talk(msg=content)
        view = step.post_ctx.get_view()
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

    def test_report(self):
        final_step = None
        for step in self.mock_agent.work(task=self.example_task, max_steps=self.mock_agent.get_report_frequency()):
            print(f'Used tool: {step.tool_outputs[0].tool_name if step.tool_outputs else None}')
            final_step = step

        update_tool_name = self.mock_agent.task_tracker.update_tool.get_name()
        print(f'Update tool name, used tool name = {update_tool_name}, {final_step.tool_outputs[0].tool_name}')
        self.assertTrue(len(final_step.tool_outputs) == 1)
        self.assertTrue(update_tool_name == final_step.tool_outputs[0].tool_name)

    def test_required_tool_use(self):
        greet_tool = Greet()
        inf_config = InfConfig(required_tool=greet_tool)
        step = self.mock_agent.handle(inf_config=inf_config)

        outputs: list[ToolOutput] = step.tool_outputs

        self.assertTrue(len(outputs) == 1)
        self.assertTrue(outputs[0].tool_name == greet_tool.get_name())

    def test_Tracker_freeze(self):
        task = Task.from_yaml(s='- Complete this task')
        work_notice = self.mock_agent.task_tracker.work_notice
        close_tool = self.mock_agent.task_tracker.close_action

        close_step = None
        for _ in self.mock_agent.work(task=task, max_steps=1):
            close_step = self.mock_agent.handle(inf_config=InfConfig.single_tool(close_tool))
            break

        gen_ctx_view = close_step.pre_ctx.get_view()
        self.assertTrue('Tracker[Active]' in gen_ctx_view)
        self.assertTrue(work_notice in gen_ctx_view)

        post_ctx_view = close_step.post_ctx.get_view()
        self.assertTrue('Tracker[Archived]' in post_ctx_view)
        self.assertTrue('Tracker[Active]' not in post_ctx_view)
        self.assertTrue(work_notice not in post_ctx_view)


class MockAgent(Agent):
    def handle(self, inf_config : InfConfig = InfConfig()) -> Step:
        context = self.get_context(inf_config=inf_config)
        if not inf_config.required_tool:
            return Step.failed(context=context, err_msg=f'No required tool provided')
        else:
            return super().handle(inf_config=inf_config)

if __name__ == "__main__":
    ta = TestAgent.ready()
    ta.execute_all()
