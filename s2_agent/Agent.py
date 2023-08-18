import os,json

import openai
from openai.openai_object import OpenAIObject
from s1_conversation.Conversation import Conversation_Participant, Dialogue_Roles, Conversation_Entry
from s1_protocol.Directive import Directive
from s1_protocol.Identity import Identity

from s2_agent.Actions import Action
from s2_agent.Tool import Tool

# ---------------------------------------------------------

class Models:
    gpt_35_16k = 'gpt-3.5-turbo-16k'
    gpt_35_4k = 'gpt-3.5-turbo'
    gpt_40_32k = 'gpt-4-32k-0613'
    gpt_40_8k = 'gpt-4-0613'


class Agent(Conversation_Participant):
    def __init__(self,api_key : str = '', model_type: str = Models.gpt_35_4k):
        # Set identity and directive
        super().__init__(role=Dialogue_Roles.agent)
        self._directive = Directive(task=None,objective=None)

        with open('../s1_protocol/IdentityDefinition/core') as idenity_file:
            core = idenity_file.read()

        with open('../s1_protocol/IdentityDefinition/principles') as principles_file:
            principles = principles_file.read()

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
            # TODO:
            # Here can try out to not register this as a system message but
            # Rather to let the agent say something like 'I read the following ...'
            # e.g. have it have an internal monologue
            tool.external_log = self.register_system_message
        self._tool_instructions = [tool.get_tool_json_doc() for tool in self.tool_list]


    # TODO: Must Confirm that the API key works after getting it
    @staticmethod
    def _get_api_key() -> str:
        try:
            key = os.environ.get('openai_key')
            if not isinstance(key,str):
                raise TypeError
        except:
            key = input('Failed to retrieve API key. Check /etc/environment for entry \’openai_key\’ and relaunch program'
                  'OR: Enter key manually and hit ENTER:')

        return key


    # ---------------------------------------------------
    # Callback

    def _reaction_protocol(self, dialogue_line : Conversation_Entry) -> None:
        if dialogue_line['role'] == Dialogue_Roles.user:
            self._process_user_request()

    # ---------------------------------------------------
    # Other

    def _process_user_request(self) -> None:
        try:
            print("[Debug] Creating completion request.")

            openai.api_key = self._api_key
            action = self._get_next_action()
            print("[Debug] Received response from the model.")

            text_content = action.get_text_content()
            tool_instructions = action.get_function_call()

            if not text_content is None:
                self.speak(message=text_content)

            if not tool_instructions is None:
                self._use_tool(instructions=tool_instructions)

        except Exception as e:
            print(f'[Error] Unable to get response from GPT-3.5. {str(e)}\n')


    def _get_next_action(self) -> Action:
        # messages = [self._identity.get_system_message()]+self.conversational_memory+[self._directive.get_msg()]
        # messages = [self._directive.get_msg()]+self.conversational_memory
        messages = [self._identity.get_msg()]+self.conversational_memory+[self._directive.get_msg()]
        openai_response = openai.ChatCompletion.create(
            model=self._model_type,
            messages=messages,
            functions=self._tool_instructions,
            function_call='auto')

        # Action is promised a dict, so a dict must be delivered in any case
        if not isinstance(openai_response,dict):
            print('[Debug]: OpenAI response is not of dictionary type. Defaulting to empty response')
            openai_response = {}

        return Action(openai_response)


    def _use_tool(self, instructions : OpenAIObject) -> None:
        if not isinstance(instructions,dict):
            print(f'[Debug]: Provided instructions {instructions} are not of dict type')
            return

        if not 'name' in instructions:
            print(f'[Debug]: Could not find name in dictionary. Aborting ... ')
            return

        if not 'arguments' in instructions:
            print(f'[Debug: Could not find arguments in dictionary. Aborting ...')
            return

        try:
            tool_args_dict = json.loads(instructions['arguments'])
        except:
            print(f'[Debug]: An error occured while trying to parse given tool arguments. Aborting ...')
            return

        tool_name = instructions['name']
        tool_dict: dict[str, Tool] = {tool.name: tool for tool in self.tool_list}

        if tool_name in tool_dict:
            tool_dict[tool_name].handle_call(args_dict=tool_args_dict)

