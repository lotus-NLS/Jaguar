import os

from engine.l0_main.settings import LotusCredentials
from engine.l1_agents.guidance.tasktracker import Task
from engine.l2_models import OpenAIModel, InfConfig
from engine.l2_models.language import Message, Context
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool, ToolArg
from holytools.devtools import Unittest

# ---------------------------------------------------

class NLU(Unittest):
    @classmethod
    def setUpClass(cls):
        configs : LotusCredentials = LotusCredentials.from_file()
        cls.model : LLM = OpenAIModel.default_model(api_key=configs.openai_api_key)
        cls.task_provider : TaskProvider = TaskProvider()

    def evaluateProperty(self, msg : str, prop : str) -> bool:
        yn = YesNoTool()
        query = (f'Please evaluate whether or not the following #property holds for the given #msg\n'
                          f'    - #property: \"{prop}\"\n'
                          f'    - #msg     : \"{msg}\"')
        entries = [Message.user(msg=query)]
        docs = [yn.get_doc()]
        context = Context(entries=entries, docs=docs)

        generation = self.model.get_generation(context=context, config=InfConfig.text_only())
        generation.exhaust()
        eval_text, calls = generation.get_text(), generation.get_tool_calls()

        context += Context.singleton(entry=Message.agent(msg=eval_text))
        options = InfConfig(required_tool=yn)
        yn_generation = self.model.get_generation(context=context, config=options)
        yn_generation.exhaust()
        text, calls = yn_generation.get_text(), yn_generation.get_tool_calls()

        self.assertTrue(len(calls) == 1)
        yn.execute(args_dict=calls[0].get_args_dict())

        print(f'Query: {query}\n'
              f'Eval : {eval_text}\n'
              f'Answer: {yn.y_n_arg.get_value()}')
        return yn.y_n_arg.get_value() == 'y'


class YesNoTool(Tool):
    def __init__(self):
        super().__init__()
        self.y_n_arg : ToolArg = ToolArg(name=f'YesOrNo', choices=[f'y', 'n'])

    def _do(self):
        pass

    def get_desc(self) -> str:
        return f'Answers the user query about the target message with yes(y) or no(n)'

    def get_args(self) -> list[ToolArg]:
        return [self.y_n_arg]


class TaskProvider:
    def __init__(self):
        script_dirpath = os.path.dirname(__file__)
        tasks_fpath = os.path.join(script_dirpath, 'tasks.txt')
        with open(tasks_fpath, 'r') as f:
            content = f.read()
            parts = content.split('++')
            parts = parts[1:]

        self.mandate_dict = {}
        for p in parts:
            lines = p.split('\n')
            name = lines[0]
            remaining = '\n'.join(lines[1:-1])
            task = Task.from_yaml(s=remaining)
            self.mandate_dict[name] = task

    def get_task(self, name : str) -> Task:
        return self.mandate_dict[name]


class EvaluationTask(NLU):
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
    EvaluationTask.execute_all()
