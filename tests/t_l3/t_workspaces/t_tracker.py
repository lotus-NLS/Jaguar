from engine.l1_agents import TaskTracker
from eval.task.resources.taskprovider import TaskProvider
from holytools.devtools import Unittest


class TestTracker(Unittest):
    def setUp(self):
        self.agent = A


    def test_autoclose(self):


        task_provider = TaskProvider()

        tracker = TaskTracker()

        tracker.open_action.execute({})
        task = task_provider.get_task(name='test')
        print(f'Task tree:\n{task.get_tree()}')

        task.complete()
        self.assertTrue(not tracker.is_active)

if __name__ == "__main__":
    TestTracker.execute_all()