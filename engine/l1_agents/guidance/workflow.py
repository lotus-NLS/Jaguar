from __future__ import annotations

import os.path
from dataclasses import dataclass

from engine.l1_agents.guidance.tasktracker import Task
from engine.l3_aos.tools import Tool, ToolArg
from holytools.fileIO import SegmentProvider

# ------------------------------------------------

@dataclass
class Node:
    name : str
    max_steps : int
    task : Task

    @classmethod
    def single_directive(cls, name : str, directive : str, max_steps : int = 5):
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
            edges.append(e)
        return edges

@dataclass
class Workflow:
    start_node: Node
    nodes : list[Node]
    edges : list[Edge]
    notice : str = ''

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

    def get_exit_tool(self, node_name : str) -> NodeNavigation:
        exit_tool = NodeNavigation(edges=self.outgoing_edge_map[node_name])
        return exit_tool

    @classmethod
    def generate_unittest(cls, project_dirpath : str, filename : str, tests_directory : str) -> Workflow:
        proj_name = os.path.basename(project_dirpath)

        notice = (f'You are tasked with creating a unittest for the file {filename} in project {proj_name}.'
                  f'You will be guided through this process through the TaskTracker tool. '
                  f'Focus only on the currently displayed tasks in the TaskTracker tool.'
                  f'As soon as you finish this section of tasks, the next secetion will be presented to you until'
                  f'the workflow is complete.')

        ys1 = (f'- Section A: Get acquinted with module {filename} \n'
               f'    - Open project: Open the project at {project_dirpath} in the PythonIDE\n'
               f'    - Open file: Open file {filename} in the PythonIDE\n'
               f'    - Analyse file {filename}: Take note of the the functionalities in {filename} that to be checked in a unittest.\n'
               f'    - List test cases: Give an informal (not code) list of cases that need to be tested via method in the unittest\n'
               f'    - Mark complete: Once the above tasks are done, complete task 1 (= sectionA) in the TaskTracker tool to proceed to the next section')
        get_acquainted_task = Task.from_yaml(s=ys1)
        n0 = Node(name='Get acquinted', task=get_acquainted_task, max_steps=25)

        ys2 = (f'- Section B: Write out unittest\n'
               f'    - Determine common resources: Make a list of resources that are shared between runs.\n'
               f'    - setUp or setUpClass: Determine whether a setUp or setUpClass routine is more appropriate.\n'
               f'    - Implement unittest: Open and write out the unittest file at the appropriate location in {tests_directory}\n'
               f'    - Fix issues: Fix any issues that appear in the inspection popup\n'
               f'    - Run: Run the test module')
        write_unittest_task = Task.from_yaml(s=ys2)
        n1 = Node(name='Write unittest', task=write_unittest_task, max_steps=20)
        edges = [Edge(source=n0, target=n1, case='Success')]


        testWorkflow = Workflow(start_node=n0, nodes=[n0, n1], edges=edges, notice=notice)
        return testWorkflow


    @classmethod
    def example(cls) -> Workflow:
        n1 = Node.single_directive(name='start', directive='Test task A. Mark this task completed')
        n2 = Node.single_directive(name='end', directive='Complete the task with taskID = 1. Do *not* under any circumstance close the TaskTracker')
        edge = Edge(source=n1, target=n2, case='Success. This workflow is just an example with a single exit case')
        return cls(start_node=n1, nodes=[n1, n2], edges=[edge], notice='You will be guided through this workflow through a series of'
                                                                       'task lists. They will each be presented to you in thie TaskTracker tool'
                                                                       'Only the active TaskTracker tool is relevant.')


class NodeNavigation(Tool):
    def __init__(self, edges : list[Edge]):
        super().__init__()
        self.edges : list[Edge] = edges
        self.exit_choice : ToolArg = ToolArg(name='Case choice', dtype=int)

    def _do(self):
        pass

    def get_desc(self) -> str:
        initial_msg = (f'Decides with which case the current task is quit. '
                       f'Please decide according to these options:\n')
        for j, e in enumerate(self.edges):
            initial_msg += f'[{j}]: {e.case}\n'
        initial_msg += f'Specify the case through an integer'
        return initial_msg

    def get_args(self) -> list[ToolArg]:
        return [self.exit_choice]


if __name__ == "__main__":
    task_provider = SegmentProvider(fpath='tasks.txt', delimiter='##')
    analyse_file = task_provider.retrieve(name=f'')

    t1 = Task.from_yaml(s=analyse_file)
    print(t1.get_tree())