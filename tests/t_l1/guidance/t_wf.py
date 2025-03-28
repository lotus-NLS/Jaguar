from engine.l1_agents import Task
from engine.l1_agents.guidance.workflow import Workflow, NodeNavigation, Node, Edge
from holytools.devtools import Unittest


class TestWorkflow(Unittest):
    def setUp(self):
        self.workflow : Workflow = Workflow.example()

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
        nodeA = Node(name='StepA', max_steps=3, task=Task.get_example())
        nodeB = Node(name='StepB', max_steps=3, task=Task.get_example())
        nodes = [nodeA]
        edges = [Edge(source=nodeA, target=nodeB, case='Success')]

        with self.assertRaises(KeyError):
            self.invalid_wf: Workflow = Workflow(start_node=nodeA, nodes=nodes, edges=edges)

if __name__ == "__main__":
    TestWorkflow.execute_all()
