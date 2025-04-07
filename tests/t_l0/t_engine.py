from engine.l0_main.lotus_engine import LotusEngine
from engine.l1_agents import Workflow
from holytools.devtools import Unittest


class TestEngine(Unittest):
    def setUp(self):
        self.engine : LotusEngine = LotusEngine()

    def test_do_workflow(self):
        wf = Workflow.example()
        final_node = self.engine.do_workflow(wf=wf)
        self.assertTrue(final_node.name == 'end')
        self.assertTrue(final_node.task.is_recursively_complete())

if __name__ == '__main__':
    TestEngine.execute_all()