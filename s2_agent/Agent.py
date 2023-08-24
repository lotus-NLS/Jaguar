import os

import openai
# from openai.openai_object import OpenAIObject
from s2_agent.Actions import ToolInstructions
from s1_conversation.Conversation import ConversationParticipant, Dialogue_Roles, ConversationEntry
from s1_protocol.Directive import Directive
from s1_protocol.Identity import Identity


from s2_agent.Actions import Action
from s2_agent.Tool import Tool

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


class Agent(ConversationParticipant):
    def __init__(self,api_key : str = '', model_type: str = Models.gpt_40_8k):
        # Set identity and directive
        super().__init__(role=Dialogue_Roles.agent)
        self._directive = Directive(task=None,objective=None)

        with open('../s1_protocol/IdentityDefinition/core') as idenity_file:
            core = idenity_file.read()

        # Reconsider this later
        # with open('../s1_protocol/IdentityDefinition/principles') as principles_file:
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

    def add_tool_list(self, tool_list : list[Tool]) -> None:
        self.tool_list += tool_list
        for tool in tool_list:
            tool.external_log = self.think
        self._tool_instructions = [tool.get_tool_json_doc() for tool in self.tool_list]


    @staticmethod
    def _get_api_key() -> str:
        try:
            key = os.environ.get('openai_key')
            if not isinstance(key, str):
                raise TypeError
        except:
            key = input(
                'Failed to retrieve API key. Check /etc/environment for entry \’openai_key\’ and relaunch program'
                'OR: Enter API key manually and hit ENTER to continue:\n')

        try:
            openai.Completion.create(
                api_key=key,
                engine="davinci",
                prompt="This is a test.",
                max_tokens=5
            )
        except Exception as e:
            print(f'The given key raised the following error after test run:\n'
                  f' {e}')
            print(f'Aborting ...')
            raise ValueError

        return key

    # ---------------------------------------------------
    # Callback

    def _reaction_protocol(self, dialogue_line : ConversationEntry) -> None:
        if dialogue_line['role'] == Dialogue_Roles.user:
            self._process_user_request()

    # ---------------------------------------------------
    # Other

    def _process_user_request(self) -> None:
        try:
            print("[Debug] Creating completion request.")
            action = self._get_next_action()
            print("[Debug] Received response from the model.")

            text_content = action.get_text_content()
            tool_instructions = action.get_tool_instructions()

            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_instructions is None:
                self._use_tool(instructions=tool_instructions)

        except Exception as e:
            print(f'[Error] Unable to get response from GPT-3.5. {str(e)}\n')


    def _get_next_action(self) -> Action:
        openai.api_key = self._api_key
        messages = [self._identity.get_msg()]+self._personal_log

        args_dict = {
            'model' : self._model_type,
            'messages' : messages,
            'temperature' : 0.2
        }

        if not len(self.tool_list) == 0:
            args_dict['functions'] = self._tool_instructions
            args_dict['function_call'] = 'auto'

        openai_response = openai.ChatCompletion.create(**args_dict)

        # Action is promised a dict, so a dict must be delivered in any case
        if not isinstance(openai_response,dict):
            print('[Debug]: OpenAI response is not of dictionary type. Defaulting to empty response')
            openai_response = {}

        return Action(openai_response)


    def _use_tool(self, instructions : ToolInstructions) -> None:
        print('[Debug]: agent requested tool usage')
        tool_name = instructions.name
        tool_args_dict = instructions.arguments

        tool_dict: dict[str, Tool] = {tool.name: tool for tool in self.tool_list}
        if tool_name in tool_dict:
            tool_dict[tool_name].handle_call(args_dict=tool_args_dict)

