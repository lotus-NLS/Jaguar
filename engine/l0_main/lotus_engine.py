import time

from engine.l0_main.lotus_io import LotusIO
from engine.l0_main.settings import LotusCredentials
from engine.l1_agents import Agent
from engine.l1_agents.tasks.task import Task
from engine.l1_agents.workflows.workflow import Workflow, Node
from engine.l2_models import OpenAIModel, InfConfig
from engine.l2_models.language import Message
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from engine.l3_aos.tools import Tool
from holytools.logging import Timber

# ---------------------------------------------------------

class LotusEngine(Timber):
    def __init__(self):
        super().__init__()
        self._creds: LotusCredentials = LotusCredentials.auto()

        model = OpenAIModel.default_model(api_key=self._creds.openai_api_key)
        self.agent : Agent = self.make_agent(model=model)
        self.IO : LotusIO = LotusIO(disable_socket=True)

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
            msg = Message.user(text='Hello world')
            self.IO.outgoing_messages.put(msg)

    def do_workflow(self, wf : Workflow) -> Node:
        node = wf.start_node
        workflow_description = Message.system(text=wf.notice)
        self.agent.update_memory(entry=workflow_description)

        while True:
            self.info(f'\n## Now starting work on node: {node.name}')
            self.do_task(task=node.mandate, max_turns=node.max_turns)
            if not node.name in wf.source_edge_map:
                break
            else:
                outgoing_edges = wf.source_edge_map[node.name]

            exit_tool = wf.get_exit_tool(node_name=node.name)
            self.agent.update_memory(entry=Message.tool(text=exit_tool.get_desc(), name=exit_tool.get_name()))
            iterator = self.agent.step(inf_config=InfConfig(required_tool=exit_tool))
            _ = iterator.__next__()
            __ = iterator.__next__()

            choice = exit_tool.exit_choice.get_value()
            node = outgoing_edges[choice].target

        return node

    def do_task(self, task : Task, max_turns : int, halt_every_step : bool = False):
        self.info(f'- {Agent.__name__}.{Agent.work.__name__}: Starting work on task')
        writings : list[str] = []
        for step in self.agent.work(task=task, max_turns=max_turns):
            w = self.IO.observe(step=step)
            writings.append(w)

            if halt_every_step:
                time.sleep(0.02)
                input(f'Press enter to continue ...')

        self.info(f'- Finished work mode after {len(writings)} steps\n')

    def do_talk(self, query : str) -> str:
        user_mesage = Message.user(text=query)
        self.IO.send(user_mesage)

        text = ''
        for step in self.agent.talk(msg=query):
            text += self.IO.observe(step=step)
        return text

    def use_tool(self, tool : Tool, view : str, task : str):
        view = Message.system(text=view)
        task_msg = Message.system(text=task)

        agent = self.make_agent(model=self.agent.model)
        agent.memory = [view, task_msg]
        step = agent.use(tool=tool)
        self.IO.observe(step=step)


if __name__ == "__main__":
    engine = LotusEngine()
    engine.testroutine()