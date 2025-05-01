from eval.zcenarios.taskprovider import TaskProvider
from holytools.devtools import Unittest
from tests.basetests import AgentTest

# ---------------------------------------------------

class TestTaskProvider(Unittest):
    def test_retrieval(self):
        provider = TaskProvider()
        task = provider.get_task(identifier='test')
        tree = task.get_tree()
        print(f'- Task tree:\n"{tree}"')
        self.assertTrue('Test' in tree)
        self.assertTrue(len(tree.split('\n')) == 1)


class TestTracker(AgentTest):
    def test_no_root(self):
        tracker = self.agent.task_tracker
        with self.assertRaises(ValueError):
            tracker.open()

    def test_autoclose(self):
        task_provider = TaskProvider()
        task = task_provider.get_task(identifier='test')

        tracker = self.agent.task_tracker
        tracker.root = task
        tracker.open_action.execute({})

        print(f'Task tree:\n{task.get_tree()}')
        tracker.complete_task(task_id='1')

        self.assertTrue(not tracker.is_open)

if __name__ == "__main__":
    # TestTracker.execute_all()
    TestTaskProvider.execute_all()