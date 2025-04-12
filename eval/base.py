import json

import fuzzywuzzy.fuzz

from engine.l0_main.lotus_engine import LotusEngine
from engine.l0_main.settings import LotusCredentials
from engine.l2_models import OpenAIModel, InfConfig
from engine.l2_models.language import Message, Context
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool, ToolArg
from eval.zcenarios.taskprovider import TaskProvider
from holytools.devtools import Unittest

# ---------------------------------------------------

class NLU(Unittest):
    @classmethod
    def setUpClass(cls):
        configs : LotusCredentials = LotusCredentials.from_file()
        cls.model : LLM = OpenAIModel.default_model(api_key=configs.openai_api_key)
        cls.task_provider : TaskProvider = TaskProvider()
        cls.engine : LotusEngine = LotusEngine()

    def evaluateProperty(self, msg : str, prop : str) -> bool:
        yn = YesNoTool()
        query = (f'Please evaluate whether or not the following #property holds for the given #msg\n'
                          f'    - #property: \"{prop}\"\n'
                          f'    - #msg     : \"{msg}\"')
        entries = [Message.user(msg=query)]
        docs = [yn.get_doc()]
        context = Context(messages=entries, docs=docs)

        generation = self.model.get_generation(context=context, config=InfConfig.text_only())
        generation.exhaust()
        eval_text, calls = generation.get_text(), generation.get_tool_calls()

        context += Context.singleton(entry=Message.agent(msg=eval_text))
        yn_inf_config = InfConfig(required_tool=yn)
        yn_generation = self.model.get_generation(context=context, config=yn_inf_config)
        yn_generation.exhaust()
        text, calls = yn_generation.get_text(), yn_generation.get_tool_calls()

        self.assertTrue(len(calls) == 1)
        yn.execute(args_dict=calls[0].get_args_dict())

        print(f'\n- Evaluation results:')
        print(f'Query: {query}\n'
              f'Eval : {eval_text}\n'
              f'Answer: {yn.y_n_arg.get_value()}')
        return yn.y_n_arg.get_value() == 'y'


class TaskUnittest(NLU):
    def setUp(self):
        self.engine.reset()

    def semantic_task_eval(self, task_name : str, query : str, prop : str) -> bool:
        task = self.task_provider.get_task(task_name)
        self.engine.do_task(task=task, max_steps=10)
        response = self.engine.do_talk(query=query)

        return self.evaluateProperty(msg=response, prop=prop)

    def keyword_task_eval(self, task_name : str, query : str, keyword : str, fuzzy : bool = False) -> bool:
        task = self.task_provider.get_task(task_name)
        self.engine.do_task(task=task, max_steps=10)

        self.engine.agent.update_memory(entry=Message.user(msg=query))
        tool = KeywordProviderTool()
        inf_config = InfConfig(required_tool=tool)
        self.engine.agent.handle(inf_config=inf_config)
        given_keyword = tool.keyword_arg.get_value()

        print('\n-> Keyword task evaluation:')
        print(f'- Given keyword: {given_keyword}'
              f'\n- Expected keyword: {keyword}')

        if fuzzy:
            tol = 75
            accuracy = fuzzywuzzy.fuzz.ratio(given_keyword, keyword)
            print(f'- Fuzzy accuracy: {accuracy}')
            return accuracy > tol
        else:
            return given_keyword == keyword

    def dict_task_eval(self, task_name : str, query : str, target_dict : dict[str, str]):

        class DictProviderTool(Tool):
            def __init__(self):
                super().__init__()
                self.tool_args_dict = {}
                for key in target_dict:
                     self.tool_args_dict[key] = ToolArg(name=key)

            def get_desc(self) -> str:
                return f'Allows you to fill in the value for every #key'

            def get_args(self) -> list[ToolArg]:
                return list(self.tool_args_dict.values())

            def _do(self):
                pass

        task = self.task_provider.get_task(task_name)
        self.engine.do_task(task=task, max_steps=10)
        self.engine.agent.update_memory(entry=Message.user(msg=query))

        tool = DictProviderTool()
        inf_config = InfConfig(required_tool=tool)
        self.engine.agent.handle(inf_config=inf_config)

        given_dict = {}
        for k in target_dict:
            given_dict[k] = tool.tool_args_dict[k].get_value()

        print(f'- Given dictionary: {json.dumps(given_dict, indent=2)}')
        print(f'- Target dictionary: {json.dumps(target_dict, indent=2)}')

        dict_equals = json.dumps(given_dict, sort_keys=True) == json.dumps(target_dict, sort_keys=True)
        return dict_equals

class KeywordProviderTool(Tool):
    def __init__(self):
        super().__init__()
        self.keyword_arg : ToolArg = ToolArg(name=f'Keyword', dtype=str)

    def _do(self):
        pass

    def get_desc(self) -> str:
        return f'Fill in the #keyword if you were successful in learning it in the prior step'

    def get_args(self) -> list[ToolArg]:
        return [self.keyword_arg]


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

#
#
# import unittest
#
# from holytools.devtools import Unittest
# from holytools.devtools.testing.runner import Runner
#
#
# class StatisticalUnittest(Unittest):
#     @classmethod
#     def execute_all(cls, reps : int, tolerance : float):
#         result_arr = []
#
#         for _ in range(reps):
#             suite = unittest.TestLoader().loadTestsFromTestCase(cls)
#             runner = Runner(logger=cls.get_logger(), test_name=cls.__name__)
#             results = runner.run(testsuite=suite)
#             result_arr.append(results)
#
#
#         case_0_results = [result.case_reports[0].status for result in result_arr]
#         checkmark_arr = ['✓' if result.lower() == 'Success'.lower() else '✗' for result in case_0_results]
#
#         print(f'-> Results:')
#         print(f'- Cases: {checkmark_arr}')
#         err_ratio = checkmark_arr.count("✗") / len(checkmark_arr)
#         if err_ratio < tolerance:
#             symbol = '<'
#         elif (err_ratio-tolerance) < 1e-3:
#             symbol = '='
#         else:
#             symbol = '>'
#         print(f'- Error ratio:  {err_ratio} {symbol} {tolerance}')
#         print(f'- Verdict: {"OK" if err_ratio < tolerance else "FAIL"}')
#
#     def test_sometimes_ok(self):
#         import random
#         if random.random() < 0.25:
#             self.assertTrue(True)
#         else:
#             self.assertTrue(False)
#
#     def test_often_ok(self):
#         import random
#         if random.random() < 0.75:
#             self.assertTrue(True)
#         else:
#             self.assertTrue(False)
#
# if __name__ == "__main__":
#     StatisticalUnittest.execute_all(reps=5, tolerance=0.5)
#     # StatisticalUnittest.execute_all()