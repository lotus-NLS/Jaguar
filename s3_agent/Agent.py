import os
from typing import Type

import openai
from s3_agent.Actions import ToolInstructions
from s4_conversation.s0_ConversationParticipant import ConversationParticipant, DialogueRole
from s4_conversation.s2_ConversationEntry import ConversationEntry
from s4_protocol.Directive import Directive
from s4_protocol.Identity import Identity


from s3_agent.Actions import Action
from s3_agent.Tool import Tool

# ---------------------------------------------------------

class Models:
    # The 0613 models (06.13.23, the date of the
    # API updates (https://openai.com/blog/function-calling-and-other-api-updates)
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
    def __init__(self,api_key : str = '', model_type: str = Models.gpt_40_8k):
        # Set identity and directive
        super().__init__(role=DialogueRole.agent())
        self._directive = Directive(task=None,objective=None)

        with open('../s4_protocol/IdentityDefinition/core') as idenity_file:
            core = idenity_file.read()

        # Reconsider this later
        # with open('../s4_protocol/IdentityDefinition/principles') as principles_file:
        #     principles = principles_file.read()

        self._identity = Identity(core=core,principles='')

        # Set model
        self._model_type : str = model_type
        self._api_key : str = api_key if not api_key == '' else self._get_api_key()

        # Set up tools
        self.tool_list : list[Tool] = []
        self._tool_instructions : list[dict] = []

    # ---------------------------------------------------
    # Setup

    def set_tools(self, tool_classes : list[Type[Tool]]) -> None:
        def tool_logger(msg : str):
            self.log_entry(ConversationEntry(role=DialogueRole.tool(),msg=msg))

        self.tool_list += [tool() for tool in tool_classes]
        for tool in self.tool_list:
            tool.external_log = tool_logger
        self._tool_instructions = [tool.get_tool_json_doc() for tool in self.tool_list]

    # TODO: get_api_key needs to be OS independent and set the api_key for only one user
    def _get_api_key(self) -> str:
        try:
            key = os.environ.get('openai_key')
            if not isinstance(key, str):
                raise TypeError
        except:
            key = input(
                'Failed to retrieve API key. Check /etc/environment for entry \’openai_key\’ and relaunch program'
                'OR: Enter API key manually and hit ENTER to continue:\n')

        try:
            openai.api_key = key
            args_dict = {
                'model': self._model_type,
                'messages': [ConversationEntry(role=DialogueRole.user(),msg='This is a test')],
            }
            openai.ChatCompletion.create(**args_dict)

        except Exception as e:
            print(f'The given key raised the following error after test run:\n'
                  f' {e}')
            print(f'Aborting ...')
            raise ValueError

        return key

    # ---------------------------------------------------
    # Callback

    def _reaction_protocol(self, dialogue_line : ConversationEntry) -> None:
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


    def get_next_action(self, is_allowed_functioncall = True) -> Action:
        openai.api_key = self._api_key
        messages = [self._identity.get_msg()]+self._personal_log

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

        return Action(openai_response)


    def _use_tool(self, instructions : ToolInstructions) -> None:
        print('[Debug]: Agent requested tool usage')
        tool_name = instructions.name
        tool_args_dict = instructions.arguments

        self.think(f'I called the tool {tool_name} with the arguments {tool_args_dict}')

        tool_dict: dict[str, Tool] = {tool.name: tool for tool in self.tool_list}
        if tool_name in tool_dict:
            tool_dict[tool_name].handle_call(args_dict=tool_args_dict)


        self.think(f'I must update the user on the results of the tool usage')
        text_content = self.get_next_action(is_allowed_functioncall=False).get_text_content()
        if not text_content is None:
            self.speak(msg=text_content)




