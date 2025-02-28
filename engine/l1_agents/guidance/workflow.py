from __future__ import annotations
from dataclasses import dataclass

from engine.l1_agents import Task
from engine.l3_aos.tools import Tool, ToolArg

# ------------------------------------------------

@dataclass
class Node:
    content : str
    max_steps : int
    task : Task
    exit_cases : list[ExitCase]

    def get_exit_tool(self) -> ExitTool:
        return ExitTool(exit_cases=self.exit_cases)

@dataclass
class ExitCase:
    description : str
    target_node : Node


@dataclass
class Workflow:
    start_node: Node
    nodes : list[Node]

    # @classmethod
    # def get_example_workflow(cls) -> Workflow:
    #     start_node = Node(content='Start', max_steps=3, task=Task.get_example_task())
    #     nodes = [start_node]
    #     return cls(start_node=start_node, nodes=nodes)


class ExitTool(Tool):
    def __init__(self, exit_cases : list[ExitCase]):
        super().__init__()
        self.exit_cases : list[ExitCase] = exit_cases
        self.exit_choice : ToolArg = ToolArg(name='Exit choice', dtype=int)

    def do(self):
        pass

    def get_desc(self) -> str:
        initial_msg = f'Decides with which case the current task is quit:'
        for j, c in enumerate(self.exit_cases):
            initial_msg += f'\n[{j}]: {c.description}\n'
        return initial_msg

    def get_args(self) -> list[ToolArg]:
        return [self.exit_choice]


if __name__ == "__main__":
    pass