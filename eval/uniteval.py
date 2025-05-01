import json

import fuzzywuzzy.fuzz

from engine.l2_models import InfConfig
from engine.l2_models.language import Message
from engine.l3_aos.tools import Tool, ToolArg
from eval.nlu import NLU

# ---------------------------------------------------

class Uniteval(NLU):
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

    def dict_task_eval(self, task_name : str, query : str, target_dict : dict[str, str], fuzzy : bool = False) -> bool:
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

        dicts_match = True
        fuzzy_tol = 70
        for k in given_dict:
            v1, v2 = given_dict[k], target_dict[k]
            values_match = self.values_match(v1, v2, fuzzy=fuzzy, fuzzy_tol=fuzzy_tol)
            if not values_match:
                dicts_match = False
            if not values_match and fuzzy:
                print(f'- Fuzzy ratio {fuzzywuzzy.fuzz.ratio(v1, v2)} below tol {fuzzy_tol} for key "{k}": \n'
                      f'    - Given value : "{v1}"\n'
                      f'    - Target value: "{v2}"')

        return dicts_match

    @staticmethod
    def values_match(v1: str, v2: str, fuzzy : bool, fuzzy_tol : int = 75):
        if '|' in v2:
            v21, v22 = v2.split('||')
            v21_match = Uniteval.values_match(v1, v21, fuzzy=fuzzy, fuzzy_tol=fuzzy_tol)
            v22_match = Uniteval.values_match(v1, v22, fuzzy=fuzzy, fuzzy_tol=fuzzy_tol)
            return v21_match or v22_match

        if fuzzy:
            match = fuzzywuzzy.fuzz.ratio(v1, v2) > fuzzy_tol
        else:
            match = v1 == v2
        return match

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


