from engine import LotusEngine
from engine.l1_agents import Workflow



class UnittestEval:
    def __init__(self):
        self.unittest_workflow = Workflow.generate_unittest(module_name=f'Evalutor and YesNoTool in evaluator.py',
                                                       tests_directory='tests',
                                                       project_dirpath=f'/home/daniel/lotus/engine')
