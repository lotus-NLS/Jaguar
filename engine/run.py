from engine.l0_main.lotus_engine import LotusEngine
from engine.l1_agents import Workflow

if __name__ == "__main__":
    engine = LotusEngine()

    engine.do_talk()

    unittest_workflow = Workflow.unittest(filename=f'Evalutor and YesNoTool in evaluator.py',
                                          tests_directory='tests',
                                          project_dirpath=f'/home/daniel/lotus/engine')
    engine.do_workflow(wf=unittest_workflow)
