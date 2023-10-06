from typing import Optional
from abc import abstractmethod
from src.l3_lotus_core import LingualEntity, DialogueRole, Entry, get_exception_msg


from src.l2_lotus_agent.m0_agent.task import TaskQueue, Task
from src.l2_lotus_agent.m0_agent.tool_handler import ToolHandler
from src.l2_lotus_agent.m2_protocol import Mandate, Identity, Cores
from src.l2_lotus_agent.m1_models import OpenAIModel, LLM, OpenAI_ModelTypes, Action, ActionOptions, FunctCallOption

# ---------------------------------------------------------

class Agent(LingualEntity):
    @classmethod
    def make_website_summarization_agent(cls):
        return Agent(identity=Identity(core=Cores.website_information_retriever),
                     model_type=OpenAIModel(OpenAI_ModelTypes.gpt_35_4k))

    @classmethod
    def make_report_composition_agent(cls):
        return Agent(identity=Identity(Cores.report_composer), model_type=OpenAIModel(OpenAI_ModelTypes.gpt_35_4k))


    def __init__(self, model_type : LLM = OpenAIModel(OpenAI_ModelTypes.gpt_40_8k) , identity : Identity = Identity(core=Cores.goto)):
        LingualEntity.__init__(self, role=DialogueRole.agent_role())

        # Set identity, mandate and task queue
        self.identity : Identity = identity
        self.mandate : Mandate = Mandate.make_empty()
        self.task_queue : TaskQueue[Task] = TaskQueue()

        # Set tool handler
        self.tool_handler : ToolHandler = ToolHandler()

        # Set llm
        self.model : LLM = model_type

    # ---------------------------------------------------
    # Main routine

    @abstractmethod
    def launch(self):
        pass

    @abstractmethod
    def loop(self):
        pass

    @abstractmethod
    def react(self, entry : Entry):
        pass


    def do(self, required_funct_name : Optional[str] = None):
        try:
            arg_dict = {
                'call_allowed' : True,
                'required_funct_name' : required_funct_name
            }

            action = self.get_next_action(
                funct_call_options=FunctCallOption(**arg_dict),
                additional_entries=[self.get_active_task_entry()]
            )

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

    # ---------------------------------------------------
    # Actions

    def handle_tool_response(self, err_text : Optional[str] = None):
        if not err_text is None:
            self.think(get_exception_msg(text=err_text))

        if self.task_queue.view_active_task().is_dialogue_task():
            log_msg = ('##Automatic message: The user has been provided with the function output. Please provide the user with an update'
                       'In your update it is not necessary to provide the user with the function output')
            feedback_msg = self.get_next_action(
                funct_call_options=FunctCallOption.make_no_call_option(),
                additional_entries=[Entry(role=DialogueRole.user_role(),msg=log_msg)]).get_text()
            self.speak(feedback_msg)


    def get_response(self, max_tokens : int, entries : Optional[list[Entry]] = None) -> str:
        return self.get_next_action(funct_call_options=FunctCallOption.make_no_call_option(),
                                    max_tokens=max_tokens).get_text()


    def get_next_action(self,
                        funct_call_options : FunctCallOption = FunctCallOption.make_auto_option(),
                        custom_tool_docs : Optional[list[dict]] = None,
                        max_tokens : Optional[int] = None,
                        temperature : float = 0.3,
                        additional_entries : Optional[list[Entry]] = None) -> Action:

        if additional_entries is None:
            additional_entries = []

        action = self.model.get_action(
            entries=self.get_basic_entries()+additional_entries,
            tool_docs=self.tool_handler.get_active_tool_docs() if custom_tool_docs is None else custom_tool_docs,
            action_options=ActionOptions(funct_call_options=funct_call_options,max_tokens=max_tokens,temperature=temperature)
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
            task_entry = Entry(DialogueRole.system_role(), msg=self.mandate.get_msg())
        else:
            task_entry = Entry(DialogueRole.user_role(), msg=f'Respond to unread messages:\n{self.get_unread_as_str()}')

        return task_entry

