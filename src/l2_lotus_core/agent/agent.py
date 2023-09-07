from typing import Type, Union, Optional
import openai

from src.l2_lotus_core.conversation.conversation_participant import ConversationParticipant, DialogueRole
from src.l2_lotus_core.protocol.priming import Priming
from src.l2_lotus_core.agent.actionplan import ActionPlan
from src.l2_lotus_core.agent.tool import Tool, ToolInstructions
from src.l2_lotus_core.settings.constants import Models


# ---------------------------------------------------------

class FunctionCallModes:
    auto = 'auto'
    none = 'none'

class Agent(ConversationParticipant):
    def __init__(self, model_type: str = Models.gpt_40_8k, priming : Priming = None):
        super().__init__(role=DialogueRole.agent())

        # Set identity and directive
        self._priming = priming if not priming is None else Priming.make_goto_priming()

        # Set model
        self._model_type : str = model_type

        # Set up tools
        self.tool_list : list[Tool] = []
        self._tool_instructions : list[dict] = []

    # ---------------------------------------------------
    # Setup

    def set_tools(self, tool_types : list[Type[Tool]]) -> None:
        # TODO: Need to log not just tool role but tool name as well
        self.tool_list += [tool() for tool in tool_types]
        for tool in self.tool_list:
            tool.external_log = self.log_tool_msg
        self._tool_instructions = [tool.get_tool_json_doc() for tool in self.tool_list]


    # ---------------------------------------------------
    # Callback

    def _reaction_protocol(self, dialogue_line) -> None:
        if dialogue_line['role'] == DialogueRole.user():
            self._perform_next_action()

    # ---------------------------------------------------
    # Other

    def _perform_next_action(self) -> None:
        try:
            print("[Debug]: Creating completion request.")
            action = self.get_next_action()
            print("[Debug]: Received response from the model.")

            text_content = action.get_text_content()
            tool_instructions = action.get_tool_instructions()

            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_instructions is None:
                self._use_tool(instructions=tool_instructions)

        except Exception as e:
            print(f'[Error] Unable to get response from {self._model_type}. {str(e)}\n')


    def _use_tool(self, instructions : ToolInstructions) -> None:
        print('[Debug]: Agent requested tool usage')
        tool_name = instructions.name
        tool_args_dict = instructions.arguments

        tool_dict: dict[str, Tool] = {tool.name: tool for tool in self.tool_list}
        if tool_name in tool_dict:
            tool_dict[tool_name].handle_call(args_dict=tool_args_dict)


        self.think(f'I must update the user on the results of the tool usage')
        text_content = self.get_next_action(is_allowed_functioncall=False).get_text_content()
        if not text_content is None:
            self.speak(msg=text_content)

    def get_next_action(self, is_allowed_functioncall : bool = True, max_tokens : Optional[int] = None, temperature : float = 0.3) -> ActionPlan:
        core_entry = ConversationParticipant.make_entry(role=DialogueRole.system(), msg=self._priming.get_identity_msg())
        messages = [core_entry]+self._personal_log

        args_dict = {
            'model' : self._model_type,
            'messages' : messages,
            'temperature' : temperature
        }

        if not len(self.tool_list) == 0:
            args_dict['functions'] = self._tool_instructions
            args_dict['function_call'] =  FunctionCallModes.auto if is_allowed_functioncall else FunctionCallModes.none

        if not max_tokens is None:
            args_dict['max_tokens'] = max_tokens

        openai_response = openai.ChatCompletion.create(**args_dict)

        # Action is promised a dict, so a dict must be delivered in any case
        if not isinstance(openai_response,dict):
            print('[Debug]: OpenAI response is not of dictionary type. Defaulting to empty response')
            openai_response = {}

        return ActionPlan(openai_response)


class SinglePurposeAgent(Agent):

    @classmethod
    def make_website_summarization_agent(cls):
        return cls(priming=Priming.make_website_summarization_priming(), model_type=Models.gpt_35_4k)

    @classmethod
    def make_report_composition_agent(cls):
        return cls(priming=Priming.make_report_composition_priming(), model_type=Models.gpt_35_4k)

    def __init__(self, priming: Priming, model_type=Models.gpt_35_4k):
        super().__init__(model_type=model_type,priming=priming)

    def _reaction_protocol(self, dialogue_line) -> None:
        pass

    def get_text_response(self, prompt : str) -> str:
        self.log_user_msg(msg=prompt)
        text_response = self.get_next_action(is_allowed_functioncall=False).get_text_content()

        if text_response is None:
            print('[Error]: Could not obtain text response from single purpose agent. Returning empty string')
            text_response = ''

        return text_response