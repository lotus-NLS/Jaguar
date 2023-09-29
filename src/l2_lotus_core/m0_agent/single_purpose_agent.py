from typing import Optional

from src.l2_lotus_core.m0_agent.agent import Agent
from src.l2_lotus_core.m1_models import OpenAIModel, LLM
from src.l2_lotus_core.m1_protocol import Identity, Cores

# ---------------------------------------------------------

class SinglePurposeAgent(Agent):
    @classmethod
    def make_website_summarization_agent(cls):
        return cls(identity=Identity(core=Cores.website_information_retriever), model_type=OpenAIModel.make_gpt_35_4k())

    @classmethod
    def make_report_composition_agent(cls):
        return cls(identity=Cores.report_composer, model_type=OpenAIModel.make_gpt_35_4k())

    def __init__(self, identity: Identity, model_type : LLM):
        super().__init__(model_type=model_type, identity=identity)

    def react(self, conv_entry) -> None:
        pass

    def get_text_response(self, prompt : str, max_token : Optional[int] = None, verbose = True) -> str:
        self.log_user_msg(msg=prompt)
        self.log_system_msg(f'Your next message is limited to {max_token} tokens')
        text_response = self.get_next_action(is_allowed_functcall=False, max_tokens=max_token).get_text()
        self.think(text_response, verbose=verbose)

        if text_response is None:
            print('[Error]: Could not obtain text response from single purpose agent. Returning empty string')
            text_response = ''

        return text_response
