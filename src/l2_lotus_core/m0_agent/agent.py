from typing import Optional
import traceback
import threading

from src.l2_lotus_core.m0_agent.task import TaskQueue, Task
from src.l2_lotus_core.m1_models import ToolInstruction
from src.l2_lotus_core.m2_base_tool.base_tool import BaseTool
from src.l2_lotus_core.m2_protocol import Mandate, Identity, Cores
from src.l2_lotus_core.m1_models import Action, ActionOptions
from src.l2_lotus_core.m1_models import OpenAIModel, LLM, OpenAI_ModelTypes
from src.l2_lotus_core.m2_conversation import ConversationParticipant, DialogueRole, Entry

# ---------------------------------------------------------

# TODO : This together with the tool logging should be an extra logging package smth. like customlogging
def get_err_msg(text: str):
    return (f'[Error]: {text}\n'
            f'{traceback.format_exc()}')


class Agent(ConversationParticipant):
    def __init__(self, model_type : LLM = OpenAIModel(OpenAI_ModelTypes.gpt_40_8k) , identity : Identity = Identity(core=Cores.goto)):
        ConversationParticipant.__init__(self, role=DialogueRole.agent_role())

        # Set identity, mandate and task queue
        self.identity : Identity = identity
        self.mandate : Mandate = Mandate.make_empty()
        self.task_queue : TaskQueue[Task] = TaskQueue()

        # Set up toolbox
        self.tool_dict : dict[str,BaseTool] = {}

        self.model : LLM = model_type

        # Launch
        self.launch()


    def launch(self):
        threading.Thread(target=self.loop).start()

    # ---------------------------------------------------
    # Main routine

    def loop(self):
        while True:
            self.task_queue.get()
            entries_to_process = self.get_unread_entries()

            self.do()

            if self.mandate.is_active() and not self.task_queue.get_work_task_present():
                self.task_queue.put(Task(is_mandate_task=True))

            for entry in entries_to_process:
                entry.mark_read()

            self.task_queue.complete_active_task()


    def react(self, entry : Entry) -> None:
        if entry.get_role() == DialogueRole.user_role() and not self.task_queue.get_dialogue_task_present():
            self.task_queue.put(Task(is_mandate_task=False))


    def do(self) -> None:
        try:
            action = self.get_next_action(additional_entries=[self.get_task_entry()])

        except Exception:
            print(get_err_msg(text=f'Unable to obtain response from {self.name}'))
            return

        try:
            text_content = action.get_text()
            tool_instructions = action.get_tool_instructions()

        except Exception:
            self.handle_tool_response(err_text=f'An error occured while trying to parse tool call arguments or text')
            return

        try:
            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_instructions is None:
                self.use_tool(instructions=tool_instructions)

        except Exception:
            self.handle_tool_response(err_text=f'The following error occured while trying to perform action:\nAction: {action}')


    def use_tool(self, instructions : ToolInstruction) -> None:
        print('[Debug]: Agent requested tool usage')
        tool_name = instructions.name
        tool_args_dict = instructions.arguments

        if tool_name in self.tool_dict:
            self.tool_dict[tool_name].handle_call(args_dict=tool_args_dict)

        feedback_msg = ('##Automatic message: The user has been provided with the function output. Please provide the user with an update'
                        'In your update it is not necessary to provide the user with the function output')
        additional_entries = [Entry(role=DialogueRole.user_role(),msg=feedback_msg)]
        feedback_msg = self.get_next_action(is_allowed_functcall=False,additional_entries= additional_entries).get_text()
        self.speak(feedback_msg)


    def handle_tool_response(self, err_text : Optional[str] = None):
        if not err_text is None:
            self.think(get_err_msg(text=err_text))

        feedback_msg = self.get_next_action(is_allowed_functcall=False).get_text()
        self.speak(feedback_msg)


    def get_next_action(self,
                        is_allowed_functcall : bool = True,
                        max_tokens : Optional[int] = None,
                        temperature : float = 0.3,
                        additional_entries : Optional[list[Entry]] = None) -> Action:

        entries = self.get_basic_entries()
        if not additional_entries is None:
            entries += additional_entries

        action = self.model.get_action(
            entries=entries,
            tool_docs=self.get_active_tool_docs(),
            action_options=ActionOptions(is_allowed_functioncall=is_allowed_functcall,max_tokens=max_tokens,temperature=temperature)
        )

        return action

    # ---------------------------------------------------
    # Context

    def get_basic_entries(self) -> list[Entry]:
        core_entry = Entry(role=DialogueRole.system_role(), msg=self.identity.get_str())
        return [core_entry] + self._personal_log


    def get_task_entry(self) -> Optional[Entry]:
        task = self.task_queue.view_active_task()
        if task is None:
            task_entry = None

        else:
            if task.is_mandate_task():
                task_entry = Entry(DialogueRole.system_role(), msg=self.mandate.get_str())
            else:
                unread_entries_text = 'Respond to unread messages: '
                for entry in self.get_unread_entries():
                    unread_entries_text += str(entry)

                task_entry = Entry(DialogueRole.user_role(), msg= f'{unread_entries_text}')

        return task_entry


    def get_active_tool_docs(self) -> Optional[list[dict]]:
        return [tool.get_json_doc() for tool in self.tool_dict.values() if tool.is_enabled]

