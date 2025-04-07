import os

from engine.l1_agents import Workflow
from engine.l3_aos.workspaces.python_ide import ViewProvider
from eval.nlu import NLU
from eval.resources import listdir, calculator


class UnittestWFEval(NLU):
    def setUp(self):
        self.proj_dirpath: str = '/tmp/1213a3cd-7fd4-4fb0-8e3e-0c4f544d4db0'
        if not os.path.isdir(self.proj_dirpath):
            os.makedirs(self.proj_dirpath)
            python_proj = ViewProvider(project_dirpath=self.proj_dirpath)
            python_proj.mkvenv()

        calc_fpath = calculator.__file__
        listdir_fpath = listdir.__file__

        self.copy_file(source_fpath=calc_fpath, dest_fpath=os.path.join(self.proj_dirpath, 'calculator.py'))
        self.copy_file(source_fpath=listdir_fpath, dest_fpath=os.path.join(self.proj_dirpath, 'listdir.py'))

    def test_calc_wf(self):
        self.engine.do_talk(query=f'Please open the python project at /tmp/1213a3cd-7fd4-4fb0-8e3e-0c4f544d4db0')

        while True:
            print()
            print(f'User: ', end='')
            user_input = input()
            self.engine.do_talk(user_input)

        # self.unittest_workflow = Workflow.generate_unittest(filename=f'Evalutor and YesNoTool in evaluator.py', tests_directory='tests',project_dirpath=f'/home/daniel/lotus/engine')

    def test_listdir_wf(self):
        self.unittest_workflow = Workflow.generate_unittest(filename=f'ListDir',
                                                            tests_directory='eval/workflow',
                                                            project_dirpath=f'/home/daniel/lotus/engine')

    @staticmethod
    def copy_file(source_fpath : str, dest_fpath : str):
        with open(source_fpath, 'rb') as f:
            content = f.read()
            with open(dest_fpath, 'wb') as f2:
                f2.write(content)

if __name__ == "__main__":
    UnittestWFEval.execute_all()