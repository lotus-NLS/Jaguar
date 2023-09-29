from typing import Optional
from queue import Queue
import traceback
import threading

from src.l2_lotus_core.m1_models import ToolInstruction
from src.l2_lotus_core.m0_agent.tool_interface import Tool
from src.l2_lotus_core.m2_conversation import ConversationParticipant, DialogueRole, ConversationEntry
from src.l2_lotus_core.m1_protocol import Guidance, Identity, Cores
from src.l2_lotus_core.m1_models import Action, ActionOptions
from src.l2_lotus_core.m1_models import Context
from src.l2_lotus_core.m1_models import OpenAIModel


# Paradigm: Agent has work and react thread which run parallel

# ---------------------------------------------------------

# TODO : This together with the tool logging should be an extra logging package smth. like customlogging
def get_err_msg(text: str):
    return (f'[Error]: {text}\n'
            f'{traceback.format_exc()}')


class Task:
    def __init__(self, is_work_task = True):
        self._is_work_task : bool = is_work_task

    def get_is_dialogue_task(self) -> bool:
        return not self._is_work_task

    def get_is_work_task(self) -> bool:
        return self._is_work_task

    @classmethod
    def make_work_task(cls):
        return cls(is_work_task=True)

    @classmethod
    def make_dialogue_task(cls):
        return cls(is_work_task=False)


class TaskQueue(Queue):
    def __init__(self):
        super().__init__()
        self.queued_items : set = set()
        self.work_mode_enabled : bool = False

    def put(self, item : Task, block=True, timeout=None) -> None:
        super().put(item, block, timeout)
        self.queued_items.add(item)

    def get(self, block=True, timeout=None) -> Task:
        new_task = super().get(block, timeout)
        self.queued_items.remove(new_task)
        return new_task

    def work_task_present(self):
        return any(task.get_is_work_task() for task in self.queued_items)

    def dialogue_task_present(self):
        return any(task.get_is_dialogue_task() for task in self.queued_items)


class Agent(ConversationParticipant):
    def __init__(self, model = OpenAIModel.make_gpt_40_8k(), identity : Identity = None):
        super().__init__(role=DialogueRole.c_agent())

        # Set identity, guidance and task queue
        self.identity : Identity = identity if not identity is None else Identity(core=Cores.goto)
        self.guidance : Guidance = Guidance.make_empty()
        self.task_queue : TaskQueue[Task] = TaskQueue()

        # Set model
        self.model : OpenAIModel = model

        # Set up toolbox
        self.tool_dict : dict[str,Tool] = {}

        # Launch
        self.launch()

    # ---------------------------------------------------
    # Other

    def get_active_tool_context(self) -> Optional[list[dict]]:
        return [tool.get_json_doc() for tool in self.tool_dict.values() if tool.is_enabled]


    def is_in_work_mode(self):
        return self.guidance.is_active()


    def launch(self):
        threading.Thread(target=self.loop).start()

    # ---------------------------------------------------
    # Main routine

    def loop(self):
        while True:
            new_task = self.task_queue.get()

            if self.is_in_work_mode() and not self.task_queue.work_task_present():
                self.task_queue.put(Task.make_work_task())

            self.do(work_mode=new_task.get_is_work_task())


    def react(self, conv_entry : ConversationEntry) -> None:
        if conv_entry.get_role() == DialogueRole.c_user() and not self.task_queue.dialogue_task_present():
            self.task_queue.put(Task.make_dialogue_task())


    def do(self, work_mode : bool = False) -> None:
        try:
            action_content = self.get_next_action(objective_mode=work_mode)

        except Exception:
            print(get_err_msg(text=f'Unable to obtain response from {self.model.name}'))
            return

        try:
            text_content = action_content.get_text()
            tool_instructions = action_content.get_tool_instructions()

        except Exception:
            self.think(get_err_msg(text='An error occured while trying to parse tool call arguments:'))
            self.provide_feedback()
            return

        try:
            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_instructions is None:
                self.use_tool(instructions=tool_instructions)
                self.provide_feedback() if not work_mode else None

        except Exception:
            self.think(get_err_msg('The following error occured while trying to perform action:\n'
                                                 'Action: {action_content}'))
            self.provide_feedback()


    def provide_feedback(self) -> None:
        self.log_user_msg(
            f'##Automatic message: The user has been provided with the function output. Please provide the user with an update'
            f'In your update it is not necessary to provide the user with the function output'
            ,without_reaction=True)

        text_content = self.get_next_action(is_allowed_functcall=False).get_text()
        if not text_content is None:
            self.speak(msg=text_content)


    def get_next_action(self,
                        is_allowed_functcall : bool = True,
                        max_tokens : Optional[int] = None,
                        temperature : float = 0.3,
                        objective_mode : bool = False) -> Action:


        text_context = self.get_entries(work_mode=objective_mode)
        this_context = Context(msg_history=text_context, tool_docs=self.get_active_tool_context())
        this_options = ActionOptions(is_allowed_functioncall=is_allowed_functcall,
                                     max_tokens=max_tokens,
                                     temperature=temperature)

        print(f"[Debug]: Creating completion request. Token count after last response: {self.model.tokens_at_last_response}")

        print(f'[Debug]: Current conversation memory of {self.name}: [...] {str(self.get_entries())[-200:]}')
        action = self.model.get_next_action(context=this_context, action_options=this_options)
        print(f"[Debug]: Received response from the model.")

        return action


    def use_tool(self, instructions : ToolInstruction) -> None:
        print('[Debug]: Agent requested tool usage')
        tool_name = instructions.name
        tool_args_dict = instructions.arguments

        if tool_name in self.tool_dict:
            self.tool_dict[tool_name].handle_call(args_dict=tool_args_dict)


    def get_entries(self, work_mode : bool = False) -> Optional[list[ConversationEntry]]:
        core_entry = ConversationEntry(role=DialogueRole.c_system(), msg=self.identity.get_str())
        directive_entry = ConversationEntry(DialogueRole.c_system(), msg=self.guidance.get_str())
        entries = [core_entry] + self._personal_log

        if work_mode:
            entries += [directive_entry]

        return entries
