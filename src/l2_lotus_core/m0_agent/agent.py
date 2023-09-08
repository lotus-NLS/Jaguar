from typing import Type, Optional
from src.l2_lotus_core.m0_agent.tool import Tool, ToolInstruction

from src.l2_lotus_core.m1_conversation.conversation_participant import ConversationParticipant, DialogueRole
from src.l2_lotus_core.m1_protocol.priming import Priming
from src.l2_lotus_core.m1_models.actioncontent import ActionContent, ActionOptions
from src.l2_lotus_core.m1_models.model_class import LLM, Context
from src.l2_lotus_core.m1_models.model_definitions import OpenAIModel


# ---------------------------------------------------------


class Agent(ConversationParticipant):
    def __init__(self, model = OpenAIModel.make_gpt_40_8k(), priming : Priming = None):
        super().__init__(role=DialogueRole.agent())

        # Set identity and directive
        self._priming = priming if not priming is None else Priming.make_goto_priming()

        # Set model
        self._model : LLM = model

        # Set up tools
        self.tool_list : list[Tool] = []
        self._tool_docs : list[dict] = []

    # ---------------------------------------------------
    # Setup

    def set_tools(self, tool_types : list[Type[Tool]]) -> None:
        self.tool_list += [tool() for tool in tool_types]
        for tool in self.tool_list:
            def tool_log(msg : str):
                self.log_tool_msg(msg, tool_name=tool.name)
            tool.external_log = tool_log
        self._tool_docs = [tool.get_tool_json_doc() for tool in self.tool_list]

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

        except Exception as e:
            print(f'[Error]: Unable to get response from {self._model.name}. {str(e)}\n')
            return

        try:
            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_instructions is None:
                self._use_tool(instructions=tool_instructions)
        except Exception as e:
            print(f'[Error]: The following error occured while trying to perform specified action: {e}')



    def _use_tool(self, instructions : ToolInstruction) -> None:
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


    def get_next_action(self, is_allowed_functioncall : bool = True, max_tokens : Optional[int] = None, temperature : float = 0.3) -> ActionContent:

        core_entry = ConversationParticipant.make_entry(role=DialogueRole.system(),
                                                        msg=self._priming.get_identity_msg())
        messages = [core_entry] + self._personal_log
        this_context = Context(msg_history=messages, tool_docs=self._tool_docs)
        this_options = ActionOptions(is_allowed_functioncall=is_allowed_functioncall, max_tokens=max_tokens, temperature=temperature)

        return self._model.get_next_action(context=this_context,action_options=this_options)


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
        text_response = self.get_next_action(is_allowed_functioncall=False, max_tokens=max_token).get_text_content()

        if text_response is None:
            print('[Error]: Could not obtain text response from single purpose m0_agent. Returning empty string')
            text_response = ''

        return text_response