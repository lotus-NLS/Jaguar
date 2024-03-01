from __future__ import annotations
from typing import Optional
from abc import abstractmethod
import logging
from func_timeout import func_timeout, FunctionTimedOut

from api import Entry, Role
from engine.l2_models.llm import LLM, GenerationContext, Chunk, ModelType, Options
from engine.l2_models.models import OpenAIModelType

from engine.l3_applications import Application, ToolCall

# from engine.l1_agent.llm import Chunk, Action
# from engine.l1_agent.llm import ToolOptions, generation_options
from engine.l1_agent.protocol import Mandate, Identity, Core

from .task import TaskQueue, Task
from .tool_handler import OS
from ...l2_models import Options, Generation
from ...l4_singletons import ServerResponse


# ---------------------------------------------------------

class Agent(LLM):
    def __init__(self, model_type : ModelType = OpenAIModelType.GPT_4,
                       identity : Identity = Identity(core=Core.GOTO)):
        super().__init__(model_type=model_type)

        self.identity : Identity = identity
        self.task_queue : TaskQueue[Task] = TaskQueue()
        # self.mandate : Mandate = Mandate.make_empty()

        # Set tool handler
        self.os : OS = OS()
        self.log : list[Entry] = []

    # ---------------------------------------------------
    # Main routine


    def get_next(self, options: Options = Options()) -> Generation:
        context = GenerationContext(docs=self.os)

        kwargs = {
            'entries': self.get_basic_entries() if not context.entries else context.entries
            'tool_docs': self.os.get_docs_map() if custom_tool_docs is None else custom_tool_docs,
            'action_options': Options(to=tool_options, max_tokens=max_tokens, temperature=temperature)
        }

        try:
            action_stream = func_timeout(timeout=5, func=super().get_generation(context=context, options=options), kwargs=kwargs)

        except FunctionTimedOut:
            logging.info(f'Action stream request timed out. Check OpenAI server health or internet connection')
            action_stream = Generation.make_empty()

        except Exception as e:
            logging.error(f'An error occured while trying to obtain action stream: {e} Defaulting to empty action')
            action_stream = Generation.make_empty()

        return action_stream

    def do(self, task : Task):
        toolname = task.required_func

        self.os.reset_toolcall()
        action_stream = self.get_next_action_stream(
            custom_tool_docs=self.os.get_tool_doc(name=toolname),
            tool_options=ToolOptions(allowed=True, required_func=task.required_func),
            entries=self.get_basic_entries()+[task.get_entry()])


        self.handle_stream(action_stream=action_stream)
        if self.os.get_toolcall_made():
            self.handle_tool_call(task=task)


    def handle_tool_call(self, task : Task):
        self.os.handle_calls()
        if task.skip_feedback:
            return

        if task.is_dialogue_task():
            role = DialogueRole.user_role()
            log_msg = '##Automatic message: The user has been provided with the function output.Please provide the user with summary/feedback'

        else:
            role = DialogueRole.system_role()
            log_msg = f'Summarize the tool call and evaluate whether an objective has been completed'

        entries = self.get_basic_entries() + [Entry(role=role, msg=log_msg)]
        action_stream = self.get_next_action_stream(tool_options=ToolOptions.no_call(), entries=entries)
        self.handle_stream(action_stream=action_stream)


    # ---------------------------------------------------
    # Actions and context

    def get_next_action_stream(self, tool_options: ToolOptions = ToolOptions.auto(),
                               custom_tool_docs: Optional[list[dict]] = None,
                               entries: Optional[list[Entry]] = None,
                               max_tokens: Optional[int] = None,
                               temperature: float = 0.3) -> Action:




    def handle_stream(self, action_stream : Action):
        try:
            for data in action_stream:
                self.handle_chunk(chunk=data)
        except Exception as e:
            logging.error(f'An error occured while trying to handle stream: {e}')


    def handle_chunk(self, chunk : Chunk):
        try:
            text_content = chunk.get_text()
            multitool_chunk = chunk.get_call()
            is_msg_stop = text_content is None and multitool_chunk is None

            if not text_content is None:
                self.enqueue(msg=text_content)
            elif is_msg_stop:
                self.enqueue(msg='',final=True)

            if not multitool_chunk is None:
                self.os.multi_tool_call.update_from_multi(new_multicall=multitool_chunk)
        except:
            logging.info(f'An error occured while trying to parse chunk')


    def get_basic_entries(self) -> list[Entry]:
        basic_entries = [Entry(role=DialogueRole.system_role(), msg=self.identity.get_str())]
        basic_entries += self._personal_log

        return basic_entries
