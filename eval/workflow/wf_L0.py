import os

from engine.l1_agents import Workflow
from engine.l3_aos.workspaces.python_ide import PythonIDE
from eval.base import NLU
import eval.workflow.resources.listdir as listdir
import eval.workflow.resources.calculator as calculator

class UnittestWFEval(NLU):


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



if __name__ == "__main__":
    UnittestWFEval.execute_all()