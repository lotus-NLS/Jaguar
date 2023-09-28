from src.l1_lotus_tools.m0_tool_class.tool import ToolArg, Tool
from src.l2_lotus_core.m1_protocol import Objective
# from src.l2_lotus_core.m1_protocol import Directive
import inspect
from typing import Optional

# ---------------------------------------------------------


# TODO: Dynamic argument currently simply wont work; This will require adjusting self.arguments accordingly
class UPDATE_GUIDANCE(Tool):
    def __init__(self):
        super().__init__()

        self.root_objective : Optional[Objective] = None
        self.description : str = 'This tools allows you to mark an objective as complete'
        self.objective_uuid_arg: ToolArg = self.create_arg(name='objective_id', dtype=str,
                                                           desc='The ID of the objective that you want to update')

        self.action_type_arg : Optional[ToolArg] = None
        self.description_arg: ToolArg = self.create_arg(name='desc', dtype=str, is_optional=True,
                                                        desc=f'Required for {Objective.edit_desc.__name__} and {Objective.make_subelement.__name__}'
                                                             f'to specify the edited description or description of the new element')

    def enable(self):
        super().enable()
        self.root_objective = self.acting_agent.guidance.root_objective

        function_names = self.root_objective.available_actions.keys()


        self.action_type_arg: ToolArg = self.create_arg(name='action', dtype=str,
                                                        available_options=[func_name for func_name in function_names],
                                                        desc='The type of action that you want to perform')


    def do(self):
        objective_to_edit = self.root_objective.get_objective(objective_key=self.objective_uuid_arg.val)
        action = objective_to_edit.available_actions[self.action_type_arg.val]

        action_args = self.get_callable_args(action)

        if 'desc' in action_args:
            action(desc=self.description_arg.val)

        else:
            action()

        if not self.acting_agent.guidance.root_objective.is_active:
            self.acting_agent.guidance.root_objective = None

            init_tool = self.acting_agent.all_tool_dict[INITIALIZE_GUIDANCE.__name__]
            init_tool.enable()
            self.disable()


    @staticmethod
    def get_callable_args(func : callable):
        func_sig = inspect.signature(func)
        params = list(func_sig.parameters.keys())
        return params

# ---------------------------------------------------------


class INITIALIZE_GUIDANCE(Tool):
    def __init__(self):
        super().__init__()

        self.desc : str = ('This tools allows you to initialize a directive by supplying a'
                           ' root objectives and a tree of subobjectives in a list')

        self.content_arg : ToolArg =  self.create_arg(name='Objective specifications', dtype=str
                                                      , desc="""Specify your objectives in this format; Note that there is only a single root objective:
                                                                    Root Objective
                                                                    -Sub-objective
                                                                    -Sub-objective
                                                                    --Sub-sub objective
                                                                    - Sub-objective
                                                                    -- Sub-sub objective""")


    def do(self) -> None:
        directive = self.acting_agent.guidance
        if directive.is_active():
            self.semantic_error(f'There is still an active directive so directive cannot be initialized. Aborting ...')
            return

        objective_str = self.content_arg.val
        objective_lines = objective_str.split('\n')

        format_valid = self.is_valid_format(lines=objective_lines)
        if not format_valid:
            self.semantic_error(f'The given objective specifcations do not fit the required format')
            return

        stack : list[Objective] = []
        for line in objective_lines:
            indent_level, content = self.get_leading_dashes_count(line), line.lstrip('-')

            if indent_level == 0:
                new_objective = Objective.make_root(desc=f'{content}')
                directive.root_objective = new_objective
            else:
                stack = stack[:indent_level]
                new_objective = stack[-1].make_subelement(desc=f'{content}')

            stack.append(new_objective)

        update_tool = self.acting_agent.all_tool_dict[UPDATE_GUIDANCE.__name__]
        update_tool.enable()
        self.disable()

        # TODO
        print(f'Temp debug: Currently acting agent root objective: {self.acting_agent.guidance.root_objective}')


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