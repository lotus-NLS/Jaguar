from typing import Optional

from src.l2_lotus_agent.m0_agent.agent import Agent
from src.l2_lotus_agent.m1_models import OpenAIModel, LLM, OpenAI_ModelTypes
from src.l2_lotus_agent.m2_protocol import Identity, Cores

# ---------------------------------------------------------
#
# TODO: Remove this class. Agent is entirely sufficient for what it attempts to do
class SinglePurposeAgent(Agent):
#     @classmethod
#     def make_website_summarization_agent(cls):
#         return cls(identity=Identity(core=Cores.website_information_retriever), model_type=OpenAIModel(OpenAI_ModelTypes.gpt_35_4k))
#
#     @classmethod
#     def make_report_composition_agent(cls):
#         return cls(identity=Identity(Cores.report_composer), model_type=OpenAIModel(OpenAI_ModelTypes.gpt_35_4k))
#
#     def __init__(self, identity: Identity, model_type : LLM):
#         super().__init__(model_type=model_type, identity=identity)
#
    def loop(self):
        pass

    def launch(self):
        pass

    def react(self, entry):
        pass
#
#     def think(self,msg : str, verbose = False):
#         super().think(msg,verbose=verbose)
#
#     def get_text_response(self, prompt : str, max_token : Optional[int] = None) -> str:
#         self.log_user_msg(msg=prompt)
#         self.log_system_msg(f'Your next message is limited to {max_token} tokens')
#         text_response = self.get_next_action(is_allowed_functcall=False, max_tokens=max_token).get_text()
#         self.think(text_response)
#
#         if text_response is None:
#             print('[Error]: Could not obtain text response from single purpose agent. Returning empty string')
#             text_response = ''
#
#         return text_response
