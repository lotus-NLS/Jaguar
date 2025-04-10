from eval.zcenarios.taskprovider import TaskProvider
from holytools.devtools import Unittest


class TestTaskProvider(Unittest):
    def test_retrieval(self):
        provider = TaskProvider()
        task = provider.get_task(identifier='test')
        tree = task.get_tree()
        print(f'- Task tree:\n{tree}')
        self.assertTrue('Test' in tree)
        self.assertTrue(len(tree.split('\n')) == 1)

    def test(self):
        pass

if __name__ == "__main__":
    TestTaskProvider.execute_all()