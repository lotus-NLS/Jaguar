from typing import Optional
import traceback
import threading

from src.l2_lotus_core.m0_agent.task import TaskQueue, Task
from src.l2_lotus_core.m1_models import ToolInstruction
from src.l2_lotus_core.m0_agent.tool_interface import Tool
from src.l2_lotus_core.m1_protocol import Mandate, Identity, Cores
from src.l2_lotus_core.m1_models import Action, ActionOptions
from src.l2_lotus_core.m1_models import OpenAIModel, LLM, OpenAI_ModelTypes
from src.l2_lotus_core.m2_conversation import ConversationParticipant, DialogueRole, Entry

# ---------------------------------------------------------

# TODO : This together with the tool logging should be an extra logging package smth. like customlogging
def get_err_msg(text: str):
    return (f'[Error]: {text}\n'
            f'{traceback.format_exc()}')


class Agent(ConversationParticipant):
    def __init__(self, model_type : LLM = OpenAIModel(OpenAI_ModelTypes.gpt_40_8k) , identity : Optional[Identity] = None):
        ConversationParticipant.__init__(self, role=DialogueRole.agent_role())

        # Set identity, mandate and task queue
        self.identity : Identity = identity if not identity is None else Identity(core=Cores.goto)
        self.mandate : Mandate = Mandate.make_empty()
        self.task_queue : TaskQueue[Task] = TaskQueue()

        # Set up toolbox
        self.tool_dict : dict[str,Tool] = {}

        self.model : LLM = model_type

        # Launch
        self.launch()


    def launch(self):
        threading.Thread(target=self.loop).start()

    # ---------------------------------------------------
    # Main routine

    def loop(self):
        while True:
            new_task = self.task_queue.get()
            is_in_work_mode = self.mandate.is_active()

            if is_in_work_mode and not self.task_queue.work_task_present():
                self.task_queue.put(Task(is_mandate_task=True))

            self.do(is_mandate=new_task.is_mandate_task())


    def react(self, entry : Entry) -> None:
        if entry.get_role() == DialogueRole.user_role() and not self.task_queue.dialogue_task_present():
            self.task_queue.put(Task(is_mandate_task=False))


    def do(self, is_mandate : bool = False) -> None:
        try:
            action = self.get_next_action(is_mandate_action=is_mandate)

        except Exception:
            print(get_err_msg(text=f'Unable to obtain response from {self.name}'))
            return

        try:
            text_content = action.get_text()
            tool_instructions = action.get_tool_instructions()

        except Exception:
            self.think(get_err_msg(text=f'An error occured while trying to parse tool call arguments or text'))
            self.continue_dialogue()
            return


        try:
            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_instructions is None:
                self.use_tool(instructions=tool_instructions)
                self.continue_dialogue()

        except Exception:
            self.think(get_err_msg(text=f'The following error occured while trying to perform action:\nAction: {action}'))
            self.continue_dialogue()


    def use_tool(self, instructions : ToolInstruction) -> None:
        print('[Debug]: Agent requested tool usage')
        tool_name = instructions.name
        tool_args_dict = instructions.arguments

        if tool_name in self.tool_dict:
            self.tool_dict[tool_name].handle_call(args_dict=tool_args_dict)

        self.log_user_msg(f'##Automatic message: The user has been provided with the function output. Please provide the user with an update'
                          f'In your update it is not necessary to provide the user with the function output'
                          ,with_reaction= False)

    def continue_dialogue(self):
        self.speak(self.get_next_action(is_allowed_functcall=False).get_text())


    def get_next_action(self,
                        is_allowed_functcall : bool = True,
                        max_tokens : Optional[int] = None,
                        temperature : float = 0.3,
                        is_mandate_action : bool = False) -> Action:

        action = self.model.get_action(
            entries=self.get_entries(work_mode_enabled=is_mandate_action),
            tool_docs=self.get_active_tool_docs(),
            action_options=ActionOptions(is_allowed_functioncall=is_allowed_functcall,max_tokens=max_tokens,temperature=temperature)
        )

        return action


    def get_entries(self, work_mode_enabled : bool = False) -> Optional[list[Entry]]:
        core_entry = Entry(role=DialogueRole.system_role(), msg=self.identity.get_str())
        mandate_entry = Entry(DialogueRole.system_role(), msg=self.mandate.get_str())
        entries = [core_entry] + self._personal_log

        if work_mode_enabled:
            entries += [mandate_entry]

        return entries


    # ---------------------------------------------------
    # Other

    def get_active_tool_docs(self) -> Optional[list[dict]]:
        return [tool.get_json_doc() for tool in self.tool_dict.values() if tool.is_enabled]
