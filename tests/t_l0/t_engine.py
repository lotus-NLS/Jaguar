from engine import LotusEngine
from engine.l1_agents import Workflow
from holytools.devtools import Unittest


class TestEngine(Unittest):
    def setUp(self):
        self.engine : LotusEngine = LotusEngine()

    def test_do_workflow(self):
        wf = Workflow.example()
        self.engine.do_workflow(wf=wf)

    def test_do_task(self):
        pass


if __name__ == '__main__':
    TestEngine.execute_all()