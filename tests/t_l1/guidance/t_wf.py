from engine.l1_agents.tasks import Task
from engine.l1_agents.workflows.workflow import Node, Edge, Workflow, NodeNavigation
from holytools.devtools import Unittest



class TestWorkflow(Unittest):
    def setUp(self):
        nodes = [Node(name='Start', mandate=Task.get_example(), max_turns=3),
                 Node(name='A', mandate=Task.get_example(), max_turns=3),
                 Node(name='B', mandate=Task.get_example(), max_turns=3), ]
        edges = [Edge(source=nodes[0], target=nodes[0], case='Success'),
                 Edge(source=nodes[0], target=nodes[2], case='Failure')]
        self.workflow = Workflow(start_node=nodes[0], nodes=nodes, edges=edges)

    def test_get_node(self):
        nodeA = self.workflow.get_node('A')
        self.assertTrue(nodeA.name == 'A')

    def test_get_outgoing(self):
        exit_tool = self.workflow.get_exit_tool('Start')
        self.assertTrue(len(exit_tool.edges) == 2)

    def test_get_exit_tool(self):
        exit_tool = self.workflow.get_exit_tool('Start')
        self.assertTrue(isinstance(exit_tool, NodeNavigation))

    def test_invalid_wf(self):
        nodeA = Node(name='StepA', max_turns=3, mandate=Task.get_example())
        nodeB = Node(name='StepB', max_turns=3, mandate=Task.get_example())
        nodes = [nodeA]
        edges = [Edge(source=nodeA, target=nodeB, case='Success')]

        with self.assertRaises(KeyError):
            self.invalid_wf: Workflow = Workflow(start_node=nodeA, nodes=nodes, edges=edges)

if __name__ == "__main__":
    TestWorkflow.execute_all()
