from typing import Optional
import threading

from src.l2_lotus_agent.m0_agent.task import TaskQueue, Task
from src.l2_lotus_agent.m0_agent.tool_handler import ToolHandler
from src.l2_lotus_agent.m2_protocol import Mandate, Identity, Cores
from src.l2_lotus_agent.m1_models import Action, ActionOptions
from src.l2_lotus_agent.m1_models import OpenAIModel, LLM, OpenAI_ModelTypes
from src.l3_lotus_core.m0_conversation import ConversationParticipant, DialogueRole, Entry
from src.l3_lotus_core.m0_logging.logger import get_exception_msg

# ---------------------------------------------------------

class Agent(ConversationParticipant):
    def __init__(self, model_type : LLM = OpenAIModel(OpenAI_ModelTypes.gpt_40_8k) , identity : Identity = Identity(core=Cores.goto)):
        ConversationParticipant.__init__(self, role=DialogueRole.agent_role())

        # Set identity, mandate and task queue
        self.identity : Identity = identity
        self.mandate : Mandate = Mandate.make_empty()
        self.task_queue : TaskQueue[Task] = TaskQueue()

        self.tool_handler : ToolHandler = ToolHandler()

        self.model : LLM = model_type

    def launch(self) -> None:
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
            action = self.get_next_action(additional_entries=[self.get_active_task_entry()])

        except Exception:
            print(get_exception_msg(text=f'Unable to obtain response from {self.name}'))
            return

        try:
            text_content = action.get_text()
            tool_action = action.get_tool_action()

        except Exception:
            self.handle_tool_response(err_text=f'An error occured while trying to parse tool call arguments or text')
            return

        try:
            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_action is None:
                self.tool_handler.use_tool(tool_action=tool_action)
                self.handle_tool_response()

        except Exception:
            self.handle_tool_response(err_text=f'The following error occured while trying to perform action:\nAction: {action}')


    def handle_tool_response(self, err_text : Optional[str] = None):
        if not err_text is None:
            self.think(get_exception_msg(text=err_text))

        if self.task_queue.view_active_task().is_dialogue_task():
            log_msg = ('##Automatic message: The user has been provided with the function output. Please provide the user with an update'
                       'In your update it is not necessary to provide the user with the function output')
            feedback_msg = self.get_next_action(
                is_allowed_functcall=False,
                additional_entries=[Entry(role=DialogueRole.user_role(),msg=log_msg)]).get_text()
            self.speak(feedback_msg)


    def get_next_action(self,
                        is_allowed_functcall : bool = True,
                        custom_tool_docs : Optional[list[dict]] = None,
                        max_tokens : Optional[int] = None,
                        temperature : float = 0.3,
                        additional_entries : Optional[list[Entry]] = None) -> Action:

        if additional_entries is None:
            additional_entries = []

        action = self.model.get_action(
            entries=self.get_basic_entries()+additional_entries,
            tool_docs=self.tool_handler.get_active_tool_docs() if custom_tool_docs is None else custom_tool_docs,
            action_options=ActionOptions(is_allowed_functioncall=is_allowed_functcall,max_tokens=max_tokens,temperature=temperature)
        )

        return action

    # ---------------------------------------------------
    # Context

    def get_basic_entries(self) -> list[Entry]:
        core_entry = Entry(role=DialogueRole.system_role(), msg=self.identity.get_str())
        return [core_entry] + self._personal_log


    def get_active_task_entry(self) -> Optional[Entry]:
        task = self.task_queue.view_active_task()

        if task is None:
            return None

        if task.is_mandate_task():
            task_entry = Entry(DialogueRole.system_role(), msg=self.mandate.get_str())
        else:
            task_entry = Entry(DialogueRole.user_role(), msg=f'Respond to unread messages:\n{self.get_unread_as_str()}')

        return task_entry


