from __future__ import annotations
from dataclasses import dataclass

from engine.l1_agents import Task
from engine.l3_aos.tools import Tool, ToolArg

# ------------------------------------------------

@dataclass
class Node:
    name : str
    max_steps : int
    task : Task

@dataclass
class Edge:
    source : Node
    target : Node
    case : str


@dataclass
class Workflow:
    start_node: Node
    nodes : list[Node]
    edges : list[Edge]

    def __post_init__(self):
        self.node_map : dict[str, Node] = {}
        for n in self.nodes:
            if n.name in self.node_map:
                raise ValueError(f'Node with name {n.name} already exists')
            self.node_map[n.name] = n

        self.outgoing_edge_map : dict[str, list[Edge]] = {}
        for e in self.edges:
            if not e.source.name in self.outgoing_edge_map:
                self.outgoing_edge_map[e.source.name] = []
            self.outgoing_edge_map[e.source.name].append(e)

    def get_exit_tool(self, node_name : str) -> ExitTool:
        exit_tool = ExitTool(edges=self.outgoing_edge_map[node_name])
        return exit_tool

    @classmethod
    def get_example_workflow(cls) -> Workflow:
        nodeA = Node(name='A', max_steps=3, task=Task.get_example())
        nodeB = Node(name='B', max_steps=3, task=Task.get_example())
        start_node = Node(name='Start', max_steps=3, task=Task.get_example())

        edges = [Edge(source=start_node, target=nodeA, case='Success'),
                 Edge(source=start_node, target=nodeB, case='Failure')]

        nodes = [start_node]
        return cls(start_node=start_node, nodes=nodes, edges=edges)


class ExitTool(Tool):
    def __init__(self, edges : list[Edge]):
        super().__init__()
        self.edges : list[Edge] = edges
        self.exit_choice : ToolArg = ToolArg(name='Exit choice', dtype=int)

    def do(self):
        pass

    def get_desc(self) -> str:
        initial_msg = (f'Decides with which case the current task is quit. '
                       f'Please decide according to these options:')
        for j, e in enumerate(self.edges):
            initial_msg += f'\n[{j}]: {e.case}'
        return initial_msg

    def get_args(self) -> list[ToolArg]:
        return [self.exit_choice]


if __name__ == "__main__":
    wf = Workflow.get_example_workflow()
    tool = wf.get_exit_tool(node_name='Start')
    print(tool.get_desc())
    print(tool.get_args())
