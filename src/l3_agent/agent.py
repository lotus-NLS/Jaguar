from typing import Type
import openai

from src.l5_conversation.l0_conversation_participant import ConversationParticipant, DialogueRole
from src.l4_protocol.priming import Priming
from src.l3_agent.actionplan import ActionPlan
from src.l3_agent.tool import Tool, ToolInstructions

# ---------------------------------------------------------

class Models:
    # The 0613 models (06.13.23, the date of the API updates (https://openai.com/blog/function-calling-and-other-api-updates)
    # support function calling
    # But gpt-4 or gpt-3.5-turbo will always point to the newest version anyway

    gpt_35_4k = 'gpt-3.5-turbo-0613'
    gpt_35_16k = 'gpt-3.5-turbo-16k-0613'
    gpt_40_8k = 'gpt-4-0613'
    gpt_40_32k = 'gpt-4-32k-0613'

class FunctionCallModes:
    auto = 'auto'
    none = 'none'


class Agent(ConversationParticipant):
    def __init__(self,model_type: str = Models.gpt_40_8k, priming : Priming = None):
        super().__init__(role=DialogueRole.agent())

        # Set identity and directive
        if priming is None:
            self._priming = Priming.initialize_from_file()

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


    def get_next_action(self, is_allowed_functioncall = True) -> ActionPlan:
        core_entry = ConversationParticipant.get_entry(role=DialogueRole.system(),msg=self._priming.get_identity_msg())
        messages = [core_entry]+self._personal_log

        args_dict = {
            'model' : self._model_type,
            'messages' : messages,
            'temperature' : 0.3
        }

        if not len(self.tool_list) == 0:
            args_dict['functions'] = self._tool_instructions
            args_dict['function_call'] =  FunctionCallModes.auto if is_allowed_functioncall else FunctionCallModes.none

        openai_response = openai.ChatCompletion.create(**args_dict)

        # Action is promised a dict, so a dict must be delivered in any case
        if not isinstance(openai_response,dict):
            print('[Debug]: OpenAI response is not of dictionary type. Defaulting to empty response')
            openai_response = {}

        return ActionPlan(openai_response)


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

