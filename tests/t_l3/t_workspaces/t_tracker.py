from eval.task.resources.taskprovider import TaskProvider
from tests.basetests import AgentTest

# ---------------------------------------------------

class TestTracker(AgentTest):
    def test_no_root(self):
        tracker = self.agent.task_tracker
        with self.assertRaises(ValueError):
            tracker.open()

    def test_autoclose(self):
        task_provider = TaskProvider()
        task = task_provider.get_task(name='test')

        tracker = self.agent.task_tracker
        tracker.root = task
        tracker.open_action.execute({})

        print(f'Task tree:\n{task.get_tree()}')
        tracker.complete_task(task_id='1')

        self.assertTrue(not tracker.is_active)

if __name__ == "__main__":
    TestTracker.execute_all()