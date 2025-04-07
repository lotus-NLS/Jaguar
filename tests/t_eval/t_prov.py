from eval.task.resources.taskprovider import TaskProvider
from holytools.devtools import Unittest


class TestTaskProvider(Unittest):
    def test_retrieval(self):
        provider = TaskProvider()
        task = provider.get_task(name='test')
        print(f'- Task content = {task._content}')
        self.assertTrue('Test' in task._content)


if __name__ == "__main__":
    TestTaskProvider.execute_all()