from src.l2_lotus_core.m0_agent.tool import Tool, ToolArg
from src.l2_lotus_core.m1_protocol import Directive, Objective


class UPDATE_DIRECTIVE(Tool):
    def __init__(self, directive : Directive):
        super().__init__()

        self.directive = directive

        self.description : str = 'Update directive tool allows you to mark down objectives along which you will carry out your actions'


class INITIALIZE_DIRECTIVE(Tool):
    def __init__(self, directive : Directive):
        super().__init__()

        self.directive : Directive = directive

        self.desc : str = 'This tools allows you to initialize a directive by supplying a root objectives and a tree of subobjectives in a list'

        self.directive_content : ToolArg =  self.create_arg(name='Objective specifications',dtype=str
                                                        ,desc="""Specify your objectives in this format; Note that there is only a single root objective: 
                                                              Root Objective
                                                              - Sub-objective
                                                              - Sub-objective
                                                              -- Sub-sub objective
                                                              - Sub-objective
                                                              -- Sub-sub objective""")


    def do(self) -> None:
        if not self.directive.is_empty():
            self.semantic_error(f'There is still an active directive so directive cannot be initialized. Aborting ...')
            return

        objective_str = self.directive_content.val
        objective_lines = objective_str.split('\n')

        format_valid = self.is_valid_format(lines=objective_lines)
        if not format_valid:
            self.semantic_error(f'The given objective specifcations do not fit the required format')
            return

        stack : list[Objective] = []
        for line in objective_lines:
            indent_level, content = self.get_leading_dashes_count(line), line.lstrip('-')

            if indent_level == 0:
                new_objective = Objective.make_root(name=f'{content}')
                self.directive.root_objective = new_objective
            else:
                stack = stack[:indent_level]
                new_objective = stack[-1].make_subelement(name=f'{content}')

            stack.append(new_objective)

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