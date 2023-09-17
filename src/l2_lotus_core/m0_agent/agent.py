from typing import Type, Optional
from src.l2_lotus_core.m0_agent.tool import Tool
from src.l2_lotus_core.m1_models.action import ToolInstruction

from src.l2_lotus_core.m2_conversation import ConversationParticipant, DialogueRole
from src.l2_lotus_core.m1_protocol import Priming
from src.l2_lotus_core.m1_models import Action, ActionOptions
from src.l2_lotus_core.m1_models import LLM, Context
from src.l2_lotus_core.m1_models import OpenAIModel

# ---------------------------------------------------------


class Agent(ConversationParticipant):
    def __init__(self, model = OpenAIModel.make_gpt_40_8k(), priming : Priming = None):
        super().__init__(role=DialogueRole.agent())

        # Set identity and directive
        self._priming = priming if not priming is None else Priming.make_goto_priming()

        # Set model
        self.model : OpenAIModel = model

        # Set up tools
        self.tool_list : list[Tool] = []
        self._tool_docs : Optional[list[dict]] = None

    # ---------------------------------------------------
    # Setup

    def set_tools(self, tool_types : list[Type[Tool]]) -> None:
        self.tool_list += [tool() for tool in tool_types]
        for tool in self.tool_list:
            tool.external_log = self.get_tool_logger(tool_name=tool.name)

        self._tool_docs = [tool.get_tool_json_doc() for tool in self.tool_list]

    # ---------------------------------------------------
    # Other

    def _reaction_protocol(self, dialogue_line) -> None:
        if dialogue_line['role'] == DialogueRole.user():
            self._perform_next_action()

    def get_tool_logger(self,tool_name: str):
        max_tokens_tool = 1000

        def tool_log(msg: str):
            num_tokens = self.model.get_token_count(the_str=msg)

            if num_tokens > max_tokens_tool:
                msg = self.model.get_limited_string(the_str=msg, max_tokens=max_tokens_tool)

            self.log_tool_msg(msg=msg, tool_name=tool_name)

            if num_tokens > max_tokens_tool:
                warning_msg = '[Progress]: The tool output exceeded the maximum number of tokens of 1000 and was shortened to that length ...'
                self.log_tool_msg(msg=warning_msg)

        return tool_log

    # ---------------------------------------------------
    # Main routine

    def _perform_next_action(self) -> None:
        try:
            action_content = self.get_next_action()

        except Exception as e:
            print(f'[Error]: Unable to obtain response from {self.model.name}.\n{str(e)}\n')
            return

        try:
            text_content = action_content.get_text()
            tool_instructions = action_content.get_tool_instructions()
        except Exception as e:
            self.think(f'[Error]: An error occured while trying to parse tool call arguments: {e}')
            return

        try:
            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_instructions is None:
                self._use_tool(instructions=tool_instructions)

        except Exception as e:
            self.think(f'[Error]: The following error occured while trying to perform specified action {action_content}: {e}')


    def _use_tool(self, instructions : ToolInstruction) -> None:
        print('[Debug]: Agent requested tool usage')
        tool_name = instructions.name
        tool_args_dict = instructions.arguments

        tool_dict: dict[str, Tool] = {tool.name: tool for tool in self.tool_list}
        if tool_name in tool_dict:
            tool_dict[tool_name].handle_call(args_dict=tool_args_dict)

        self.log_user_msg(f'##Automatic message: The user has been provided with the function output. Please provide the user with an update'
                          f'In your update it is not necessary to provide the user with the function output'
                          ,is_without_reaction=True)
        text_content = self.get_next_action(is_allowed_functcall=False).get_text()
        if not text_content is None:
            self.speak(msg=text_content)


    def get_next_action(self,
                        is_allowed_functcall : bool = True,
                        max_tokens : Optional[int] = None,
                        temperature : float = 0.3) -> Action:

        core_entry = ConversationParticipant.make_entry(role=DialogueRole.system(),
                                                        msg=self._priming.get_identity_msg())
        messages = [core_entry] + self._personal_log
        this_context = Context(msg_history=messages, tool_docs=self._tool_docs)
        this_options = ActionOptions(is_allowed_functioncall=is_allowed_functcall,
                                     max_tokens=max_tokens,
                                     temperature=temperature)

        print("[Debug]: Creating completion request.")
        action_content = self.model.get_next_action(context=this_context, action_options=this_options)
        print(f"[Debug]: Received response from the model. Action: {action_content}")

        return action_content


class SinglePurposeAgent(Agent):
    @classmethod
    def make_website_summarization_agent(cls):
        return cls(priming=Priming.make_website_summarization_priming(), model=OpenAIModel.make_gpt_35_4k())

    @classmethod
    def make_report_composition_agent(cls):
        return cls(priming=Priming.make_report_composition_priming(), model=OpenAIModel.make_gpt_35_4k())

    def __init__(self, priming: Priming, model : LLM):
        super().__init__(model=model, priming=priming)

    def _reaction_protocol(self, dialogue_line) -> None:
        pass

    def get_text_response(self, prompt : str, max_token : Optional[int] = None) -> str:
        self.log_user_msg(msg=prompt)
        text_response = self.get_next_action(is_allowed_functcall=False, max_tokens=max_token).get_text()

        if text_response is None:
            print('[Error]: Could not obtain text response from single purpose agent. Returning empty string')
            text_response = ''

        return text_response