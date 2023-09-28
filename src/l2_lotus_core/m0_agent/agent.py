from typing import Optional
import traceback

from src.l2_lotus_core.m1_models import ToolInstruction
from src.l2_lotus_core.m0_agent.tool_interface import Tool
from src.l2_lotus_core.m2_conversation import ConversationParticipant, DialogueRole, ConversationEntry
from src.l2_lotus_core.m1_protocol import Priming, Directive
from src.l2_lotus_core.m1_models import Action, ActionOptions
from src.l2_lotus_core.m1_models import Context
from src.l2_lotus_core.m1_models import OpenAIModel

# ---------------------------------------------------------

# TODO : This together with the tool logging should be an extra logging package smth. like customlogging
def get_err_msg(text: str):
    return (f'[Error]: {text}\n'
            f'{traceback.format_exc()}')


class Agent(ConversationParticipant):
    def __init__(self, model = OpenAIModel.make_gpt_40_8k(), priming : Priming = None):
        super().__init__(role=DialogueRole.agent())

        # Set identity and directive
        self.priming : Priming = priming if not priming is None else Priming.make_goto_priming()
        self.directive : Directive = Directive.make_empty_directive()

        # Set model
        self.model : OpenAIModel = model

        # Set up toolbox
        self.all_tool_dict : dict[str,Tool] = {}

    # ---------------------------------------------------
    # Other

    def get_function_context(self) -> Optional[list[dict]]:
        return [tool.get_json_doc() for tool in self.all_tool_dict.values() if tool.is_enabled]


    def get_text_context(self, ignore_objectives : bool = False) -> Optional[list[ConversationEntry]]:
        core_entry = ConversationEntry(role=DialogueRole.system(),msg=self.priming.get_identity_str())
        directive_entry = ConversationEntry(DialogueRole.system(),msg=self.directive.get_str())
        text_context = [core_entry] + self._personal_log

        if not ignore_objectives:
            text_context += [directive_entry]

        return text_context


    def is_in_dialogue_mode(self):
        return not self.directive.is_active()

    # ---------------------------------------------------

    def _reaction_protocol(self, dialogue_line) -> None:
        if dialogue_line['role'] == DialogueRole.user():
            self.perform_next_action()


    # Main routine
    def perform_next_action(self) -> None:
        try:
            action_content = self.get_next_action()

        except Exception:
            print(get_err_msg(text=f'Unable to obtain response from {self.model.name}'))
            return

        try:
            text_content = action_content.get_text()
            tool_instructions = action_content.get_tool_instructions()

        except Exception:
            self.think(get_err_msg(text='An error occured while trying to parse tool call arguments:'))
            self.provide_feedback()
            return

        try:
            if not text_content is None:
                self.speak(msg=text_content)

            if not tool_instructions is None:
                self._use_tool(instructions=tool_instructions)

        except Exception:
            self.think(get_err_msg('The following error occured while trying to perform action:\n'
                                                 'Action: {action_content}'))
            self.provide_feedback()


    def _use_tool(self, instructions : ToolInstruction, is_with_feedback : bool = True) -> None:
        print('[Debug]: Agent requested tool usage')
        tool_name = instructions.name
        tool_args_dict = instructions.arguments

        if tool_name in self.all_tool_dict:
            self.all_tool_dict[tool_name].handle_call(args_dict=tool_args_dict)

        if is_with_feedback:
            self.provide_feedback()


    def provide_feedback(self) -> None:
        self.log_user_msg(
            f'##Automatic message: The user has been provided with the function output. Please provide the user with an update'
            f'In your update it is not necessary to provide the user with the function output'
            , is_without_reaction=True)

        text_content = self.get_next_action(is_allowed_functcall=False,ignore_objectives = True).get_text()
        if not text_content is None:
            self.speak(msg=text_content)


    def get_next_action(self,
                        is_allowed_functcall : bool = True,
                        max_tokens : Optional[int] = None,
                        temperature : float = 0.3,
                        ignore_objectives : bool = False) -> Action:


        text_context = self.get_text_context(ignore_objectives=ignore_objectives)
        this_context = Context(msg_history=text_context, tool_docs=self.get_function_context())
        this_options = ActionOptions(is_allowed_functioncall=is_allowed_functcall,
                                     max_tokens=max_tokens,
                                     temperature=temperature)

        print("[Debug]: Creating completion request.")
        action_content = self.model.get_next_action(context=this_context, action_options=this_options)
        print(f"[Debug]: Received response from the model.")

        return action_content



