import os

from engine.l1_agents import Workflow
from engine.l3_aos.workspaces.python_ide import PythonIDE
from eval.nlu import NLU
import scenarios.calculator
import scenarios.listdir


class UnittestWFEval(NLU):
    def setUp(self):
        self.proj_dirpath: str = '/tmp/1213a3cd-7fd4-4fb0-8e3e-0c4f544d4db0'
        if not os.path.isdir(self.proj_dirpath):
            os.makedirs(self.proj_dirpath)
            PythonIDE._mkvenv(proj_dirpath=self.proj_dirpath)

        calc_fpath = scenarios.calculator.__file__
        listdir_fpath = scenarios.listdir.__file__

        self.copy_file(source_fpath=calc_fpath, dest_fpath=os.path.join(self.proj_dirpath, 'calculator.py'))
        self.copy_file(source_fpath=listdir_fpath, dest_fpath=os.path.join(self.proj_dirpath, 'listdir.py'))

    def test_calc_wf(self):
        self.unittest_wf = Workflow.unittest(filename=f'Calculator.py',
                                             tests_directory='tests',
                                             project_dirpath=self.proj_dirpath)
        start_node = self.unittest_wf.nodes[0]
        start_task = start_node.task

        self.engine.do_task(task=start_task, max_steps=10, halt_every_step=True)


    # def test_listdir_wf(self):
    #     self.unittest_workflow = Workflow.generate_unittest(filename=f'ListDir',
    #                                                         tests_directory='eval/workflow',
    #                                                         project_dirpath=f'/home/daniel/lotus/engine')

    @staticmethod
    def copy_file(source_fpath : str, dest_fpath : str):
        with open(source_fpath, 'rb') as f:
            content = f.read()
            with open(dest_fpath, 'wb') as f2:
                f2.write(content)

if __name__ == "__main__":
    UnittestWFEval.execute_all()