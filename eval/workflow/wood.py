import os

from engine.l1_agents import Workflow
from engine.l3_aos.workspaces.python_ide import PythonProject
from eval.nlu import NLU


class UnittestWFEval(NLU):
    def __init__(self):
        super().__init__()
        self.proj_dirpath : str = '/tmp/1213a3cd-7fd4-4fb0-8e3e-0c4f544d4db0'
        if not os.path.isdir(self.proj_dirpath):
            self.setup(proj_dirpath=self.proj_dirpath)

    def test_calc_wf(self):
        self.unittest_workflow = Workflow.generate_unittest(module_name=f'Evalutor and YesNoTool in evaluator.py',
                                                            tests_directory='tests',
                                                            project_dirpath=f'/home/daniel/lotus/engine')

    def test_listdir_wf(self):
        self.unittest_workflow = Workflow.generate_unittest(module_name=f'ListDir',
                                                            tests_directory='eval/workflow',
                                                            project_dirpath=f'/home/daniel/lotus/engine')

    @staticmethod
    def setup(proj_dirpath : str):
        os.makedirs(proj_dirpath)
        python_proj = PythonProject(project_dirpath=proj_dirpath)
        python_proj.mkvenv()

if __name__ == "__main__":
    UnittestWFEval.execute_all()