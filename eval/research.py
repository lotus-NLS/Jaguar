from api import Entry
from engine import LotusEngine
from engine.l0_engine.settings import LotusCredentials
from engine.l1_agents import Workflowy
from engine.l2_models import OpenAIModel, Context, Options
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool, ToolArg
from holytools.devtools import Unittest

# ---------------------------------------------------

class YesNoTool(Tool):
    def __init__(self):
        super().__init__()
        self.y_n_arg : ToolArg = ToolArg(name=f'YesOrNo', choices=[f'y', 'n'])

    def do(self):
        pass

    def get_desc(self) -> str:
        return f'Answers the user query about the target message with yes(y) or no(n)'

    def get_args(self) -> list[ToolArg]:
        return [self.y_n_arg]


class SemanticUnittest(Unittest):
    @classmethod
    def setUpClass(cls):
        configs = LotusCredentials()
        cls.model : LLM = OpenAIModel.default_model(api_key=configs.get_openai_apikey())

    def evaluateProperty(self, msg : str, prop : str) -> bool:
        yn = YesNoTool()
        query = (f'Please evaluate whether or not the following #property holds for the given #msg\n'
                          f'    - #property: \"{prop}\"\n'
                          f'    - #msg     : \"{msg}\"')
        entries = [Entry.user(msg=query)]
        docs = [yn.get_doc()]
        context = Context(entries=entries, docs=docs)

        generation = self.model.get_generation(context=context, options=Options.text_only())
        generation.exhaust()
        text, calls = generation.get_text(), generation.get_tool_calls()
        print(f'-> Generated text: {text}')

        context += Context.singleton(entry=Entry.agent(msg=text))
        options = Options.require_call(tool_name=yn.get_name())
        yn_generation = self.model.get_generation(context=context, options=options)
        yn_generation.exhaust()
        text, calls = yn_generation.get_text(), yn_generation.get_tool_calls()

        self.assertTrue(len(calls) == 1)
        yn.execute(tool_call=calls[0])

        print(f'Query: {query}\n'
              f'Answer: {yn.y_n_arg.get_value()}')
        return yn.y_n_arg.get_value() == 'y'


class HardwareTask(SemanticUnittest):
    def test_components_there(self):
        engine = LotusEngine()
        answer = engine.resarch_routine(workflowy=Workflowy._hardware_summary(),
                                       query=f'Please give me a summary of my hardware', max_steps=5)

        property_query = ('The #msg gives information about each of the following hardware devices:'
                          f'CPU, GPU, RAM, Disks and Motherboard')
        answer = 'GOTO: '
        self.evaluateProperty(msg=answer, prop=property_query)


class EvaluationTask(SemanticUnittest):
    def test_spelling(self):
        msg = """The newly estbalsihed estate is one of the most luxurious in the entire region."""
        prop = f'The #msg contains no spelling errors'
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == False)

    def test_roman_politican(self):
        msg = """Marcus Tullius Cicero[a] (/ˈsɪsəroʊ/ SISS-ə-roh; Latin: [ˈmaːrkʊs ˈtʊlli.ʊs ˈkɪkɛroː]; 3 January 106 BC – 7 December 43 BC) was a Roman statesman, lawyer, scholar, philosopher, writer and Academic skeptic,[4] who tried to uphold optimate principles during the political crises that led to the establishment of the Roman Empire.[5] His extensive writings include treatises on rhetoric, philosophy and politics. He is considered one of Rome's greatest orators and prose stylists and the innovator of what became known as "Ciceronian rhetoric".[6][7][8] Cicero was educated in Rome and in Greece. He came from a wealthy municipal family of the Roman equestrian order, and served as consul in 63 BC."""
        prop = "The #msg describes a Roman emperor"
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == False)

    def test_mail_correspondence(self):
        msg = """Recipient: Donald Fraser
                 Sender: John Smith"""
        prop = f'The #msg is sent by Donald Fraser'
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == False)

    def test_hardware_faulty(self):
        msg = f'The motherboard is an ASRock, the disks are 2TB NVMe SSDs and the RAM is about 32GB'
        prop = f'The #msg gives information about each of the following hardware devices: CPU, GPU, RAM, Disks and Motherboard'
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == False)

    def test_hardware_valid(self):
        msg = f'The motherboard is an ASRock, the disks are 2TB NVMe SSDs and the RAM is about 32GB. The CPU is an Intel i9 and the GPU is an Nvidia RTX 3090'
        prop = f'The #msg gives information about each of the following hardware devices: CPU, GPU, RAM, Disks and Motherboard'
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == True)

if __name__ == "__main__":
    HardwareTask.execute_all()