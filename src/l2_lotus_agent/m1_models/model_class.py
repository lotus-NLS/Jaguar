from typing import Optional
from src.l2_lotus_agent.m1_models import Action, ActionOptions
from src.l3_lotus_core.m0_conversation import Entry

# ---------------------------------------------------------


# OpenAI function_call syntax: (See docs @ https://platform.openai.com/docs/guides/gpt/function-calling)
# 'auto' : Agent decides autonomously
# 'none' : No function will be called
# {"name": "<insert-function-name>"} : Enforce call of a specific function
class FunctCallOption:
    def __init__(self, call_allowed : bool = True, required_funct_name : Optional[str] = None):
        self.call_allowed : bool = call_allowed
        self.required_funct_name : Optional[str] = required_funct_name

    def get_openai_syntax(self) -> object:
        if not self.call_allowed:
            return 'none'
        if self.required_funct_name is None:
            return 'auto'
        else:
            return {'name' : f'{self.required_funct_name}'}


class LLM:
    def __init__(self, model_type: str):
        self._model_type : str = model_type

    def get_action(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
        pass


    def get_limited_string(self, the_str : str, max_tokens : int):
        pass

    def get_token_count(self,the_str: str) -> int:
        pass
