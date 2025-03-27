from engine import LotusEngine
from engine.l1_agents import Workflow

if __name__ == "__main__":
    engine = LotusEngine()

    unittest_workflow = Workflow.unittest(module_name=f'LotusEngine', tests_directory='tests')
    engine.do_workflow(wf=unittest_workflow)
