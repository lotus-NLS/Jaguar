import time

from engine.l0_main.lotus_io import LotusIO
from engine.l0_main.settings import LotusCredentials
from engine.l1_agents import Agent, Task
from engine.l1_agents.guidance.workflow import Workflow, Node
from engine.l2_models import OpenAIModel, InfConfig
from engine.l2_models.language import Message
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from holytools.logging import Timber

# ---------------------------------------------------------

class LotusEngine(Timber):
    def __init__(self):
        super().__init__()
        self._creds: LotusCredentials = LotusCredentials.auto()

        model = OpenAIModel.default_model(api_key=self._creds.openai_api_key)
        self.agent : Agent = self.make_agent(model=model)
        self.IO : LotusIO = LotusIO()

    def reset(self):
        self.agent = self.make_agent(model=self.agent.model)

    def make_agent(self, model : LLM) -> Agent:
        creds  = self._creds
        aos = AOS.full(google_api_key=creds.google_api_key, searchengine_id=creds.search_engine_id)

        return Agent(aos=aos, model=model)

    # ---------------------------------------------------------------------------------------
    # routines

    def testroutine(self):
        while True:
            time.sleep(2)
            msg = Message.user(msg='Hello world')
            self.IO.outgoing_messages.put(msg)

    def do_workflow(self, wf : Workflow) -> Node:
        node = wf.start_node
        outgoing_edges = wf.outgoing_edge_map[node.name]

        workflow_description = Message.system(msg=wf.notice)
        self.agent.update_memory(entry=workflow_description)

        while True:
            self.info(f'\n## Now starting work on node: {node.name}')
            self.do_task(task=node.task, max_steps=node.max_steps)

            if not node.name in wf.outgoing_edge_map:
                break

            exit_tool = wf.get_exit_tool(node_name=node.name)
            self.agent.update_memory(entry=Message.tool(msg=exit_tool.get_desc(), name=exit_tool.get_name()))
            self.agent.handle(inf_config=InfConfig(required_tool=exit_tool))
            choice = exit_tool.exit_choice.get_value()
            node = outgoing_edges[choice].target

        return node

    def do_task(self, task : Task, max_steps : int, halt_every_step : bool = False):
        self.info(f'- {Agent.__name__}.{Agent.work.__name__}: Starting work on task')
        writings : list[str] = []
        for step in self.agent.work(task=task, max_steps=max_steps):
            w = self.IO.observe(step=step)
            writings.append(w)

            if halt_every_step:
                time.sleep(0.02)
                input(f'Press enter to continue ...')

        self.info(f'- Finished work mode after {len(writings)} steps\n')

    def do_talk(self, query : str) -> str:
        user_mesage = Message.user(msg=query)
        self.IO.send(user_mesage)

        step = self.agent.talk(msg=query)
        response = self.IO.observe(step=step)
        return response


if __name__ == "__main__":
    engine = LotusEngine()
    engine.testroutine()