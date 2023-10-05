from typing import Optional
from src.l2_lotus_agent import ToolArg, Objective


from src.l1_lotus_tools.tool import Tool
from src.l1_lotus_tools.m1_python_utils.inspection import get_function_args
# ---------------------------------------------------------

verbose_mode = True

class UPDATE_MANDATE(Tool):
    def __init__(self):
        super().__init__()

        self.description : str = 'This tool allows you to update objectives'
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
        return self.get_root_objective().get_objective_by_id(objective_id=objective_id)


    def get_root_objective(self) -> Optional[Objective]:
        return self.acting_agent.mandate.root_objective


# ---------------------------------------------------------


class INITIALIZE_MANDATE(Tool):
    def __init__(self):
        super().__init__()

        self.desc : str = ('This tools allows you to initialize a mandate by supplying a'
                           ' root objectives and a tree of subobjectives in a list')

        self.content_arg : ToolArg =  self.create_arg(name='objective_specifications', dtype=str
                                                      , desc="""Specify your objectives in this format; Note that there is only a single root objective:
                                                                    Root Objective
                                                                    -Sub-objective
                                                                    -Sub-objective
                                                                    --Sub-sub objective
                                                                    - Sub-objective
                                                                    -- Sub-sub objective""")


    def do(self):
        mandate = self.acting_agent.mandate
        if mandate.is_active():
            self.semantic_error(f'There is still an active mandate so new mandate cannot be initialized. Aborting ...')
            return

        objective_str = self.content_arg.val
        objective_lines = objective_str.split('\n')

        # TODO: Currently asking for permission is bugged because the main loop steals the input stream
        init_request_msg = (f'Here is my plan of action for your request: '
                            f'\n{self.content_arg.val}\n'
                            f'Do you approve?')
        if not self.acting_agent.get_user_permission(request_msg=init_request_msg):
            return

        format_valid = self.is_valid_format(lines=objective_lines)
        if not format_valid:
            self.semantic_error(f'The given objective specifcations do not fit the required format')
            return

        stack : list[Objective] = []
        for line in objective_lines:
            indent_level, content = self.get_leading_dashes_count(line), line.lstrip('-')

            if indent_level == 0:
                new_objective = Objective.make_root(desc=f'{content}')
                mandate.root_objective = new_objective
            else:
                stack = stack[:indent_level]
                new_objective = stack[-1].make_subelement(desc=f'{content}')

            stack.append(new_objective)

        self.acting_agent.tool_handler.enable_tool(tool_name=UPDATE_MANDATE.__name__)
        self.disable()

        if verbose_mode:
            print(f'Temp debug: Currently acting agent root objective: {self.acting_agent.mandate.root_objective}')


    def is_valid_format(self,lines: list[str]) -> bool:
        format_correct = True

        if lines[0].startswith('-'):
            format_correct = False

        prev_indent_level = 0

        for line in lines[1:]:
            curr_indent_level = self.get_leading_dashes_count(line)

            if curr_indent_level > prev_indent_level + 1:
                format_correct = False
                break

            if not curr_indent_level > 0:
                format_correct = False
                break

            prev_indent_level = curr_indent_level

        return format_correct


    @staticmethod
    def get_leading_dashes_count(line: str) -> int:
        count = 0
        for char in line:
            if char == '-':
                count += 1
            else:
                break
        return count