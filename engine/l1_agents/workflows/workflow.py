from __future__ import annotations

import os.path
import os.path
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

import html2text

from engine.l1_agents.tasks import Task
from engine.l3_aos.tools import Tool, ToolArg


# ------------------------------------------------

@dataclass
class Node:
    name : str
    max_turns : int
    mandate : Optional[Task | Workflow]

    @classmethod
    def final(cls, name : str) -> Node:
        return Node(name=name, mandate=None, max_turns=0)

    @classmethod
    def single_directive(cls, name : str, directive : str, max_steps : int = 5):
        task = Task.from_yaml(s=f'-{directive}')
        return Node(name=name, mandate=task, max_turns=max_steps)

    @classmethod
    def from_yaml(cls, yaml_str : str,  max_steps : int):
        first_line = yaml_str.split('\n')[0]
        first_line.strip('-').strip()
        task = Task.from_yaml(s=yaml_str)
        return Node(name=first_line, mandate=task, max_turns=max_steps)

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

    @classmethod
    def from_drawio_xml(cls, xml_fpath : str, **kwargs):
        with open(xml_fpath, 'r') as f:
            xml_content = f.read()

        root = ET.fromstring(xml_content)
        mx_root = root.find('.//root')
        mx_cells = []
        for cell in mx_root.findall('mxCell'):
            cell_data = {k: v for k, v in cell.attrib.items()}
            if cell.text:
                cell_data['text'] = cell.text.strip()
            mx_cells.append(cell_data)

        drawio_edges = [e for e in mx_cells if 'edge' in e]
        drawio_vertices = [c for c in mx_cells if 'vertex' in c]

        drawio_edge_map = {e['id']: e for e in drawio_edges}
        is_true_vertex = lambda data : data['parent'] == '1'
        pseudo_vertices = [c for c in drawio_vertices if not is_true_vertex(data=c)]
        for v in pseudo_vertices:
            parent_uuid = v['parent']
            if parent_uuid in drawio_edge_map:
                e = drawio_edge_map[parent_uuid]
                e['value'] = v['value']

        node_map = {}
        true_vertices = [c for c in drawio_vertices if is_true_vertex(data=c)]
        for j, v in enumerate(true_vertices):
            uuid, parent_uuid = v['id'], v['parent']
            text = html2text.html2text(v['value'])

            leading_line = text.split('\n')[0]
            name, num_steps = leading_line.split(',')

            content_lines = text.split('\n')[2:]
            content = '\n'.join(content_lines)
            parsed_content = cls.drawio_to_yaml(content=content, variable_map=kwargs)

            task = Task.from_yaml(s=parsed_content)
            node_map[uuid] = Node(name=name, mandate=task, max_turns=num_steps)
        nodes = list(node_map.values())

        edges = []
        for j, e in enumerate(drawio_edges):
            print(f'Edge No.{j}: {e}')
            source_uuid, target_uuid = e['source'], e['target']
            case = e['value']
            source, target = node_map[source_uuid], node_map[target_uuid]

            edge = Edge(source=source, target=target, case=case)
            edges.append(edge)


        return cls(start_node=nodes[0], nodes=nodes, edges=edges)

    @staticmethod
    def drawio_to_yaml(content: str, variable_map : dict[str,str]):
        lines = content.split('\n')
        lines = [l for l in lines if l]
        temp_lines = []

        for l in lines:
            if not l.startswith('  '):
                raise ValueError(f'Invalid indentation in line "{l}"')
            temp_lines.append(l[2:])

        yaml_lines = []
        for l in temp_lines:
            sl = l.lstrip(' ')
            indentation = len(l) - len(sl)
            if not indentation % 2 == 0:
                raise ValueError(f'Invalid indentation: {l}')
            target_indent = indentation * 2
            yaml_lines.append(f' ' * target_indent + '- ' + sl)
        yaml_lines = [l.replace('* ', '') for l in yaml_lines]
        yaml_str = '\n'.join(yaml_lines)

        for name, value in variable_map.items():
            yaml_str = yaml_str.replace(f'[{name.upper()}]', value)
        return yaml_str

    def get_node(self, name : str) -> Node:
        return self.node_map[name]

    def get_exit_tool(self, node_name : str) -> NodeNavigation:
        exit_tool = NodeNavigation(edges=self.outgoing_edge_map[node_name])
        return exit_tool

    @classmethod
    def unittest(cls, project_dirpath : str, filename : str, tests_directory : str) -> Workflow:
        proj_name = os.path.basename(project_dirpath)

        notice = (f'You are tasked with creating a unittest for the file {filename} in project {proj_name}.'
                  f'You will be guided through this process through the Tracker tool. '
                  f'Focus only on the currently displayed tasks in the Tracker tool.'
                  f'As soon as you finish this section of tasks, the next secetion will be presented to you until'
                  f'the workflow is complete.')

        ys1 = (f'- Get acquinted with module {filename} \n'
               f'    - Open project: Open the project at {project_dirpath} in the PythonIDE\n'
               f'    - Open file: Open file {filename} in the PythonIDE\n'
               f'    - Analyse file {filename}: Take note of the the functionalities in {filename} that to be checked in a unittest.\n'
               f'    - List test cases: Give an informal (not code) list of cases that need to be tested via method in the unittest\n'
               f'    - Mark complete: Once the above tasks are done, complete task 1 (= sectionA) in the Tracker tool to proceed to the next section')
        get_acquainted_task = Task.from_yaml(s=ys1)
        n0 = Node(name='Get acquinted', mandate=get_acquainted_task, max_turns=25)

        ys2 = (f'- Section B: Write out unittest\n'
               f'    - Determine common resources: Make a list of resources that are shared between runs.\n'
               f'    - setUp or setUpClass: Determine whether a setUp or setUpClass routine is more appropriate.\n'
               f'    - Implement unittest: Open and write out the unittest file at the appropriate location in {tests_directory}\n'
               f'    - Fix issues: Fix any issues that appear in the inspection popup\n'
               f'    - Run: Run the test module')
        write_unittest_task = Task.from_yaml(s=ys2)
        n1 = Node(name='Write unittest', mandate=write_unittest_task, max_turns=20)
        edges = [Edge(source=n0, target=n1, case='Success')]


        testWorkflow = Workflow(start_node=n0, nodes=[n0, n1], edges=edges, notice=notice)
        return testWorkflow


    @classmethod
    def build(cls, project_dirpath : str, filename : str, description : str):
        proj_name = os.path.basename(project_dirpath)
        notice = (f'You are tasked with building an additional module in project {proj_name} in file {filename}'
                  f'Here is a description of the intended module: {description}'
                  f'{cls.get_default_notice()}')

        lib_ys = (f'- Determine suitable library if any needed'
                   f'   - Reason whether any python library is needed'
                   f'   - If library needed explore choices. Else mark done')

        build_ys = (f'- Implement an initial draft of the module'
                      f'    - Outline how you would implement these requirements'
                      f'    - Write out an initial draft of the module')

        inspection_ys = (f'- Address inspection problems'
                           f'   - Take stock of inspection issues'
                           f'   - Formulate solution and attempt to solve'
                           f'   - If unsuccessful try solution for second time'
                           f'   - If still unsucessful quit task')

        run_ys = (f'- Run and iterate until requirements fulfilled:'
                      f'    - Run  file'
                      f'    - Take note of errors or unintended behaviour'
                      f'    - Edit file to take care of errors'
                      f'    - Repeat above steps until behaviour aligns with intentions')

        lib_node = Node.from_yaml(yaml_str=lib_ys, max_steps=10)
        build_node = Node.from_yaml(yaml_str=build_ys, max_steps=10)
        inspect_node = Node.from_yaml(yaml_str=inspection_ys, max_steps=10)
        iterate_node = Node.from_yaml(yaml_str=run_ys, max_steps=10)
        inspection_issue = Node(f'Inspection failed!', mandate=None, max_turns=0)
        iterate_issue = Node(f'Iteration failed!', mandate=None, max_turns=0)
        build_success = Node(f'Build success!', mandate=None, max_turns=0)

        lib_build_edge = Edge(source=lib_node, target=build_node, case='Success')
        build_inspect_edge = Edge(source=build_node, target=inspect_node, case='Success')
        inspect_iterate_edge = Edge(source=inspect_node, target=iterate_node, case='Success')
        inspect_failure_edge = Edge(source=inspect_node, target=inspection_issue, case='Failure')
        iterate_success_edge = Edge(source=iterate_node, target=build_success, case='Success')
        iterate_failure_edge = Edge(source=iterate_node, target=iterate_issue, case='Failure')

        return Workflow(nodes=[lib_node, build_node, inspect_node, iterate_node, inspection_issue, iterate_issue, build_success],
                        edges=[lib_build_edge, build_inspect_edge, inspect_iterate_edge, inspect_failure_edge,iterate_success_edge, iterate_failure_edge],
                        start_node=lib_node,
                        notice=notice)

    @classmethod
    def edit(cls, project_dirpath : str, filepath : str, change_description : str):
        notice = (f'You are tasked with making an edit in the project {project_dirpath} in file {filepath}.'
                  f'Here is a description of the intended change: {change_description}. '
                  f'{cls.get_default_notice()}')

        planning_ys = (f'- Familiarize and outline'
                       f'   - Familiarize yourself with the classes/functions in {filepath}'
                       f'   - Outline where changes will have to be made')
        planning_task = Task.from_yaml(s=planning_ys)

        changes_ys = (f'- Implement changes'
                      f'    - Write outlined changes in file'
                      f'    - Fix inspection issues if any arise')
        changes_task = Task.from_yaml(s=changes_ys)

        planning_node = Node(name='Planning', mandate=planning_task, max_turns=10)
        changes_task = Node(name='Changes', mandate=changes_task, max_turns=10)
        edge = Edge(source=planning_node, target=changes_task, case='Success')

        return Workflow(nodes=[planning_node, changes_task],edges=[edge], notice=notice, start_node=planning_node)

    @classmethod
    def debug(cls, project_dirpath : str, filepath : str, bug_description : str):
        notice = (f'You are tasked with debugging behaviour of the file {filepath} in {project_dirpath}'
                  f'through the code state squeeze method. '
                  f'Here is a description of the bug appearing in {filepath}: {bug_description}'
                  f'The code state squeeze method involves'
                  f'creating a bugfree minimal example of the behaviour of the described module and then'
                  f'iteratively working towards the live bugful state until the bug appears to locate which lines'
                  f'introduced the bug.'
                  f'{cls.get_default_notice()}')

        familiarize_ys = (f'- Familiarize yourself with the module'
                          f'    - Open the file at {filepath}'
                          f'    - Take note of the module and its components and functions')

        minimal_example = (f'- Outline the minimal example'
                           f'   - Summarize the essential functions of this module'
                           f'   - Write out a minimal bugfree example in same directory')

        converge = (f'- Converge the minimal example against live bugful state'
                    f'  - Run the minmal minmal bugfree example'
                    f'  - Confirm that the bug is gone'
                    f'  - Iteratively introduce more components/features of the original live state')

        nodes = [Node.from_yaml(yaml_str=familiarize_ys, max_steps=10),
                Node.from_yaml(yaml_str=minimal_example, max_steps=10),
                Node.from_yaml(yaml_str=converge, max_steps=10)]

        edges = Edge.linear_chain(nodes=nodes)
        return Workflow(nodes=nodes, edges=edges, start_node=nodes[0], notice=notice)


    @classmethod
    def example(cls) -> Workflow:
        n1 = Node.single_directive(name='start', directive='Test task A. Mark this task completed')
        n2 = Node.single_directive(name='end', directive='Complete the task with taskID = 1. Do *not* under any circumstance close the Tracker')
        edge = Edge(source=n1, target=n2, case='Success. This workflow is just an example with a single exit case')
        return cls(start_node=n1, nodes=[n1, n2], edges=[edge], notice='You will be guided through this workflow through a series of'
                                                                       'task lists. They will each be presented to you in thie Tracker tool'
                                                                       'Only the active Tracker tool is relevant.')
    @classmethod
    def get_default_notice(cls) -> str:
        return (f'You will be guided through this process through the Tracker tool'
                f'Focus only on the currently displayed tasks in the Tracker tool.'
                f'As soon as you finish this section of tasks the next section will be presented to you')

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
    wf_fpath = '/home/daniel/lotus/engine/engine/l1_agents/workflows/wf.drawio'
    wf = Workflow.from_drawio_xml(xml_fpath=wf_fpath,FILEPATH='/home/daniel/somefiel.txt')
    print(wf.nodes[1].mandate.get_tree())
    print(wf.nodes[1].max_turns)
