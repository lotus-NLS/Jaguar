from __future__ import annotations
from typing import Optional
from abc import abstractmethod
from pyutils import DevLogger
from func_timeout import func_timeout

from engine.l2_agent.m1_language import LingualEntity
from api.classes.language import Entry, DialogueRole
from engine.l2_agent.m1_models import OpenAIModel, LLM, ModelTypes_OpenAI
from engine.l2_agent.m1_models import ActionChunk, ActionStream
from engine.l2_agent.m1_models import FunctCallOption, ActionOptions
from engine.l2_agent.m1_protocol import Mandate, Identity, Cores

from .task import TaskQueue, Task
from .tool_handler import ToolHandler
# ---------------------------------------------------------

class Agent(LingualEntity):
    def __init__(self, model_type : LLM = OpenAIModel(ModelTypes_OpenAI.gpt_40_8k), identity : Identity = Identity(core=Cores.goto)):
        super().__init__(role=DialogueRole.agent_role())

        # Set identity, mandate and task queue
        self.identity : Identity = identity
        self.mandate : Mandate = Mandate.make_empty()
        self.task_queue : TaskQueue[Task] = TaskQueue()

        # Set tool handler
        self.tool_handler : ToolHandler = ToolHandler()

        # Set llm
        self.model : LLM = model_type


    @abstractmethod
    def launch(self):
        pass

    @abstractmethod
    def loop(self):
        pass

    @abstractmethod
    def react(self, entry : Entry):
        pass

    # ---------------------------------------------------
    # Main routine

    def do(self, task : Task):
        try:
            toolname = task.required_funct_name
            self.tool_handler.reset_toolcall()
            action_stream = self.get_next_action_stream(
                custom_tool_docs=None if toolname is None else [self.tool_handler.get_tool_doc(name=toolname)],
                funct_call_options=FunctCallOption(call_allowed=True, required_funct_name=task.required_funct_name),
                entries=self.get_basic_entries()+[task.get_entry()])

        except Exception:
            print(DevLogger.get_exception_msg(text=f'An error occured while trying to obtain action stream from {self.name}'))
            return

        self.handle_stream(action_stream=action_stream)
        if self.tool_handler.tool_call_requested():
            self.handle_tool_call(task=task)


    def handle_tool_call(self, task : Task):
        self.tool_handler.execute_tool_call()

        if task.skip_feedback:
            return

        if task.is_dialogue_task():
            role = DialogueRole.user_role()
            log_msg = '##Automatic message: The user has been provided with the function output.Please provide the user with summary/feedback'

        else:
            role = DialogueRole.system_role()
            log_msg = f'Summarize the tool call and evaluate whether an objective has been completed'

        action_stream = self.get_next_action_stream(funct_call_options=FunctCallOption.make_no_call_option(),
                                    entries=self.get_basic_entries() + [Entry(role=role, msg=log_msg)])
        self.handle_stream(action_stream=action_stream)


    # ---------------------------------------------------
    # Actions and context

    def get_next_action_stream(self,
                               funct_call_options: FunctCallOption = FunctCallOption.make_auto_option(),
                               custom_tool_docs: Optional[list[dict]] = None,
                               entries: Optional[list[Entry]] = None,
                               max_tokens: Optional[int] = None,
                               temperature: float = 0.3) -> ActionStream:

        kwargs = {
            'entries': self.get_basic_entries() if entries is None else entries,
            'tool_docs': self.tool_handler.get_public_tool_docs() if custom_tool_docs is None else custom_tool_docs,
            'action_options': ActionOptions(funct_call_options=funct_call_options, max_tokens=max_tokens,temperature=temperature)
        }

        try:
            action_stream = func_timeout(timeout=5, func=self.model.get_action_stream, kwargs=kwargs)

        except:
            print(f'[Debug]: An error occured while trying to obtain action stream. Defaulting to empty action')
            action_stream = ActionStream.make_empty()

        return action_stream


    def handle_stream(self, action_stream : ActionStream):
        for data in action_stream:
            self.handle_chunk(chunk=data)


    def handle_chunk(self, chunk : ActionChunk):
        try:
            text_content = chunk.get_text_chunk()
            tool_chunk = chunk.get_function_chunk()
            is_msg_stop = text_content is None and tool_chunk is None

            if not text_content is None:
                self.enqueue(msg=text_content, final=False)
            elif is_msg_stop:
                self.enqueue(msg='')

            if not tool_chunk is None:
                self.tool_handler.tool_call.update(partial_tool_call=tool_chunk)
        except:
            print(f'[Debug]: An error occured while trying to parse chunk')


    def get_basic_entries(self) -> list[Entry]:
        basic_entries = []
        core_entry = Entry(role=DialogueRole.system_role(), msg=self.identity.get_str())
        basic_entries.append(core_entry)

        basic_entries += self._personal_log
        return basic_entries
