import os

from eval.task.provider import TaskProvider
from holytools.devtools import Unittest


class TestTaskProvider(Unittest):
    def test_retrieval(self):
        dirpath = os.path.dirname(__file__)
        tasks_fpath = os.path.join(dirpath, 'tasks.txt')

        provider = TaskProvider(tasks_fpath=tasks_fpath)
        task = provider.get_task(identifier='test')
        tree = task.get_tree()
        lines = tree.split('\n')

        print(f'- Task tree:\n"{tree}"')
        print(f"No. lines = {len(lines)}")
        self.assertTrue('test' in tree)
        self.assertTrue('[ ] 1:' in tree)
        self.assertTrue('\t[ ] 11:' in tree)
        self.assertTrue(len(lines) == 2)


if __name__ == "__main__":
    TestTaskProvider.execute_all()