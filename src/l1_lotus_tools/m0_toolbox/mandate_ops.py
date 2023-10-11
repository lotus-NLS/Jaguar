from typing import Optional
from src.l2_lotus_agent import ToolArg, Objective


from src.l1_lotus_tools.tool import Tool
from src.l1_lotus_tools.m1_python_utils.inspection import get_function_args
from src.l1_lotus_tools.m1_python_utils.string_formatting import get_leading_dashes_count,is_valid_hierarchy_format
# ---------------------------------------------------------

verbose_mode = True

class UPDATE_MANDATE(Tool):
    def __init__(self):
        super().__init__()

        self.description : str = 'Allows for updating objectives'
        self.objective_uuid_arg: ToolArg = self.create_arg(name='objective_id', dtype=str,
                                                           desc='The ID of the objective that you want to update')

        self.action_type_arg : Optional[ToolArg] = None
        self.description_arg: ToolArg = self.create_arg(name='desc', dtype=str, is_optional=True,
                                                        desc=f'Required for {Objective.edit_desc.__name__} and {Objective.make_subelement.__name__}'
                                                             f'to specify the edited description or description of the new element')

    def do(self):
        objective_to_edit = self.get_objective_by_id(objective_id=self.objective_uuid_arg.val)
        action = objective_to_edit.action_dict[self.action_type_arg.val]
        action_args = get_function_args(func=action)

        arg_dict = {}
        if 'desc' in action_args:
            arg_dict['desc'] = self.description_arg.val
        action(**arg_dict)

        if verbose_mode:
            print(f'[Debug]: Currently acting agent root objective:\n'f'{self.acting_agent.mandate.root_objective}')

        if not self.acting_agent.mandate.root_objective.is_active:
            self.disable()


    def enable(self):
        super().enable()
        functions = self.acting_agent.mandate.root_objective.get_available_actions()
        self.action_type_arg: ToolArg = self.create_arg(name='action', dtype=str,
                                                        available_options=[function.__name__ for function in functions],
                                                        desc='The type of action that you want to perform')

    def disable(self):
        super().disable()
        self.acting_agent.mandate.root_objective = None
        self.acting_agent.tool_handler.enable_tool(tool_name=INITIALIZE_MANDATE.__name__)


    def get_objective_by_id(self, objective_id : str):
        return self.acting_agent.mandate.root_objective.get_objective_by_id(objective_id=objective_id)


# ---------------------------------------------------------


class INITIALIZE_MANDATE(Tool):
    def __init__(self):
        super().__init__()
        self.desc : str ='Submits a request to the user to sign off on a plan of action'

        self.content_arg : ToolArg =  self.create_arg(name='objective_specifications', dtype=str,
              desc="""Specify your objectives (obj) in this format:
                      Root objective
                      -Sub obj
                      -Sub obj
                      --Sub-sub obj
                      -Sub obj
                      --Sub-sub obj""")


    def do(self):
        objective_lines = self.content_arg.val.split('\n')
        if not is_valid_hierarchy_format(lines=objective_lines):
            self.semantic_error(f'The given objective specifcations do not fit the required format')
            return

        init_request_msg = (f'Here is my plan of action for your request:'
                            f'\n{self.content_arg.val}\n'
                            f'Do you approve?')
        if not self.acting_agent.retrieve_user_permission(request_msg=init_request_msg):
            return

        self.parse_objectives_lines(lines=objective_lines)
        self.disable()

        if verbose_mode:
            print(f'[Debug]: Currently acting agent root objective:\n'f'{self.acting_agent.mandate.root_objective}')

    def disable(self):
        super().disable()
        self.acting_agent.tool_handler.enable_tool(tool_name=UPDATE_MANDATE.__name__)


    def parse_objectives_lines(self, lines : list[str]):
        stack: list[Objective] = []
        for line in lines:
            indent_level, content = get_leading_dashes_count(line), line.lstrip('-')

            if indent_level == 0:
                new_objective = Objective.make_root(desc=f'{content}')
                self.acting_agent.mandate.root_objective = new_objective
            else:
                stack = stack[:indent_level]
                new_objective = stack[-1].make_subelement(desc=f'{content}')

            stack.append(new_objective)