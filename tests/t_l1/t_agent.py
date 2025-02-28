from engine.l1_agents import Agent
from engine.l2_models import OpenAIModel, InfConfig
from engine.l3_aos import Browser, Terminal, AOS
from engine.l3_aos.tools import ToolOutput
from tests.credtest import CredTest
from tests.t_l2.base import Greet

# ------------------------------------------

class TestAgent(CredTest):
    def setUp(self):
        browser = Browser(google_api_key=self.credentials.google_api_key,
                          searchengine_id=self.credentials.search_engine_id)
        terminal = Terminal()
        aos = AOS(workspaces=[terminal, browser])
        model = OpenAIModel.default_model(api_key=self.credentials.openai_api_key)
        self.agent = Agent(aos=aos, model=model)

    def test_required_tool(self):
        greet_tool = Greet()
        inf_config = InfConfig(required_tool=greet_tool)
        step = self.agent.handle(inf_config=inf_config)

        outputs : list[ToolOutput] = step.outputs

        self.assertTrue(len(outputs) == 1)
        self.assertTrue(outputs[0].tool_name == greet_tool.get_name())



if __name__ == "__main__":
    TestAgent.execute_all()