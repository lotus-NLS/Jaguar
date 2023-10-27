from __future__ import annotations
from typing import Optional
# from lotusEngine.l3_lotus_core import LingualEntity, DialogueRole, Entry
from src.lotusEngine.l3_lotus_core import Entry
from src.lotusEngine.l2_lotus_agent.m1_models import FunctCallOption
from src.lotusEngine.l2_lotus_agent import OpenAIModel, LLM, ModelTypes_OpenAI, Agent
from src.lotusEngine.l2_lotus_agent.m1_protocol import Identity, Cores

# ----------------------------------------------------


class TextAgent(Agent):
    def launch(self):
        pass

    def loop(self):
        pass

    def react(self, entry : Entry):
        pass

    def __init__(self, identity : Identity,model_type : LLM = OpenAIModel(ModelTypes_OpenAI.gpt_35_4k)):
        super().__init__(model_type = model_type,identity=identity)

    @classmethod
    def make_website_summarization_agent(cls) -> TextAgent:
        return cls(identity=Identity(core=Cores.website_information_retriever),
                     model_type=OpenAIModel(ModelTypes_OpenAI.gpt_35_4k))


    @classmethod
    def make_report_composition_agent(cls) -> TextAgent:
        return cls(identity=Identity(Cores.report_composer), model_type=OpenAIModel(ModelTypes_OpenAI.gpt_35_4k))


    def get_text_response(self, max_tokens : Optional[int] = None, entries : Optional[list[Entry]] = None) -> str:
        arg_dict = {
            'funct_call_options' : FunctCallOption.make_no_call_option(),
            'max_tokens' : max_tokens,
            'entries' : entries
        }
        action_stream =  self.get_next_action_stream(**arg_dict)
        action_stream.exhaust()

        return action_stream.text_content