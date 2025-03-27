from __future__ import annotations
from dataclasses import dataclass

from engine.l1_agents.guidance.tasktracker import Task
from engine.l3_aos.tools import Tool, ToolArg

# ------------------------------------------------

@dataclass
class Node:
    name : str
    max_steps : int
    task : Task

    @classmethod
    def single_task(cls, name : str, directive : str, max_steps : int = 5):
        task = Task.from_yaml(s=f'-{directive}')
        return Node(name=name, task=task, max_steps=max_steps)

@dataclass
class Edge:
    source : Node
    target : Node
    case : str

    @classmethod
    def linear_chain(cls, nodes : list[Node]) -> list[Edge]:
        edges = []
        for n1, n2 in zip(nodes, nodes[1:]):
            e = Edge(source=n1, target=n2, case='Any')
        return edges

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
            if not e.source.name in self.node_map:
                raise KeyError(f'Node {e.source.name} not found')
            if not e.target.name  in self.node_map:
                raise KeyError(f'Node {e.target.name} not found')
            if not e.source.name in self.outgoing_edge_map:
                self.outgoing_edge_map[e.source.name] = []
            self.outgoing_edge_map[e.source.name].append(e)

    def get_node(self, name : str):
        return self.node_map[name]

    def get_exit_tool(self, node_name : str) -> ExitTool:
        exit_tool = ExitTool(edges=self.outgoing_edge_map[node_name])
        return exit_tool


    # @classmethod
    # def get_example_workflow(cls) -> Workflow:
    #     nodeA = Node(name='A', max_steps=3, task=Task.get_example())
    #     nodeB = Node(name='B', max_steps=3, task=Task.get_example())
    #     start_node = Node(name='Start', max_steps=3, task=Task.get_example())
    #
    #     edges = [Edge(source=start_node, target=nodeA, case='Success'),
    #              Edge(source=start_node, target=nodeB, case='Failure')]
    #
    #     nodes = [start_node, nodeA, nodeB]
    #     return cls(start_node=start_node, nodes=nodes, edges=edges)


    @classmethod
    def test_module(cls) -> Workflow:
        n1test = Node.single_task(name=f'Open files', directive=f'Open relevant module files')
        n2test = Node.single_task(name=f'Analyse file',
                                  directive=f'Take note of module functionalities that need testing.')
        n3test = Node.single_task(name=f'Write cases',
                                  directive=f'Write up test cases informally and what they will assert')
        n4test = Node.single_task(name=f'Determine common resources',
                                  directive=f'Make a list of resources that are shared between runs.'
                                            f'Determine whether a setUp or setUpClass routine is more appropriate.'
                                            f'If the tests manipulate the attributes then setUp is needed rather than setUpClass')
        n5test = Node.single_task(name=f'Implement', directive=f'Open and write out the file')
        n6test = Node.single_task(name='Run', directive=f'Run the test module')

        edgesTest = Edge.linear_chain(nodes=[n1test, n2test, n3test, n4test, n5test, n6test])
        testWorkflow = Workflow(start_node=n1test, nodes=[n1test, n2test, n3test, n4test, n5test, n6test],
                                edges=edgesTest)
        return testWorkflow


    @classmethod
    def example(cls) -> Workflow:
        n1 = Node.single_task(name='Step1', directive='Test task, please complete')
        n2 = Node.single_task(name='Step2', directive='Test task, pleaes complete')
        edge = Edge(source=n1, target=n2, case='Success')
        return cls(start_node=n1, nodes=[n1, n2], edges=[edge])


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
        initial_msg += f'Specify the case through an integer'
        return initial_msg

    def get_args(self) -> list[ToolArg]:
        return [self.exit_choice]


if __name__ == "__main__":
    wf = Workflow.example()
    tool = wf.get_exit_tool(node_name='Start')
    print(tool.get_desc())
    print(tool.get_args())
