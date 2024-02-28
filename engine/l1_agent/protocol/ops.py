import logging
# from pyutils import get_function_args

import yaml
# from engine.l1_agent import Objective, ToolArg
from abc import abstractmethod

from engine.l4_singletons import EngineIO
from engine.l3_tools.tool import Tool, ToolArg
from .mandate import Mandate

# ---------------------------------------------------------


class MandateTool(Tool):
    def __init__(self, mandate : Mandate):
        super().__init__(has_context=False)
        self.mandate : Mandate = mandate


    @abstractmethod
    def do(self):
        pass


class RequestMandate(MandateTool):
    def __init__(self, mandate : Mandate, query : Query):
        super().__init__(mandate=mandate)

        self.request_permission = request_permission
        self.desc = 'Submits a request to the user to sign off on a plan of action'
        content_desc = ("""Specify your plan of action in a YAML format e.g. like this: 
                Overall objective:
                - Sub objective 1
                - Sub objective 2
                - Sub objective 3:
                  - Sub-sub objective 1
                - Sub objective 4
                - Sub objective 5:
                  - Sub-sub objective 2""")
        self.yaml : ToolArg =  ToolArg(name='objective_specifications', desc=content_desc)

    def do(self):
        info_dict = yaml.safe_load(self.yaml.val)
        self.mandate.update(info_dict=info_dict)
        EngineIO().


class MarkDone(MandateTool):
    def __init__(self):



class UpdateMandate(MandateTool):
    def __init__(self):
        super().__init__()

        self.objective_uuid_arg: ToolArg = ToolArg(name='objective_id',
                                                   desc='The ID of the objective that you want to update')

        self.desc: ToolArg = ToolArg(name='desc', is_optional=True,
                                     desc=f'Required for {Objective.make_subelement.__name__}'
                                                             f'to specify the edited description or description of the new element')

        self.action: ToolArg = ToolArg(name='action', dtype=str,
                                       available_options=Objective.get_action_names(),
                                       desc='The type of operation that you want to perform')

    def do(self):
        objective_to_edit = self.get_objective_by_id(objective_id=self.objective_uuid_arg.val)
        operation = objective_to_edit.ops_dict[self.action.val]
        operation_args = get_function_args(func=operation)

        arg_dict = {}
        if 'desc' in operation_args:
            arg_dict['desc'] = self.desc.val
        operation(**arg_dict)

        if verbose_mode:
            logging.info(f'Currently acting agent root objective:\n'f'{self.acting_agent.mandate.root_objective}')

        if not self.acting_agent.mandate.root_objective.is_active:
            self.acting_agent.mandate.root_objective = None


    def get_objective_by_id(self, objective_id : str):
        return self.acting_agent.mandate.root_objective.get_objective_by_id(objective_id=objective_id)


# ---------------------------------------------------------


class INITIALIZE_MANDATE(Tool):
    def __init__(self):
        super().__init__()
        self.desc : str ='Submits a request to the user to sign off on a plan of action'

        self.content_arg : ToolArg =  self.create_arg(name='objective_specifications', dtype=str,
              desc="""Specify your objectives in this format. Use '-' for every item after the overall objective: 
                      Overall objective
                      - Sub objective
                      - Sub objective
                      -- Sub-sub objective
                      - Sub objective
                      -- Sub-sub objective""")


    def do(self):
        objective_lines = self.content_arg.val.split('\n')
        if not is_valid_hierarchy_format(lines=objective_lines):
            self.semantic_error(f'The given objective specifcations do not fit the required format')
            return

        init_request_msg = (f'Here is my plan of action for your request:'
                            f'\n{self.content_arg.val}\n'
                            f'Do you approve?')

        self.acting_agent.enqueue(msg=f'{init_request_msg} (y/n)')
        user_approves =  EngineIO().get_confirmation()

        if not user_approves:
            self.acting_agent.think(f'User denied permission')
            return

        self.acting_agent.think(f'User confirmed permission')
        self.parse_objectives_lines(lines=objective_lines)

        if verbose_mode:
            logging.info(f'Currently acting agent root objective:\n'f'{self.acting_agent.mandate.root_objective}')


