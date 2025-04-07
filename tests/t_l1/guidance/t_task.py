from engine.l1_agents.guidance.tasktracker import Task
from holytools.devtools import Unittest


class TestTask(Unittest):
    def setUp(self):
        self.root : Task = Task("Main Task", is_root=True)
        self.task1 = self.root.add_subtask("Task 1")
        self.task2 = self.root.add_subtask("Task 2")
        self.task3 = self.root.add_subtask("Task 3")
        self.task4 = self.root.add_subtask("Task 4")
        self.subtask11 = self.task1.add_subtask("Subtask 1.1")
        self.subtask12 = self.task1.add_subtask("Subtask 1.2")
        self.subtask13 = self.task1.add_subtask("Subtask 1.3")
        self.subtask21 = self.task2.add_subtask("Subtask 2.1")

        self.yaml_tree= (f'- Task 1\n'
                    f' -Subtask 1.1\n'
                    f' -Subtask 1.2\n'
                    f' -Subtask 1.3\n'
                    f'- Task 2')

        self.task1.complete()
        self.task4.complete()

    def test_get_Tree(self):
        tree = self.root.get_tree()
        self.assertIn(f'	[x] 12: Subtask 1.2', tree)
        self.assertIn(f'[ ] 2: Task 2',tree)

        print(f'Exmple root tree task tree:\n{tree}')

    def test_get_by_id(self):
        print(f'Name of task wiith id 1: {self.root.get_descendant("1")._content}')
        self.assertEqual(self.root.get_descendant('1')._content, self.task1._content)
        self.assertEqual(self.root.get_descendant('11')._content, self.subtask11._content)

        with self.assertRaises(ValueError):
            self.root.get_descendant('0')

    def test_complete(self):
        self.root.complete()


    def test_from_yaml_str(self):
        yaml_str = (f'- Task 1\n'
                    f'    -Subtask 1.1\n'
                    f'- Task 2')
        root = Task.from_yaml(yaml_str)
        tree = root.get_tree()

        lines = yaml_str.split()
        print(f'Yaml generated task tree: \n{tree}')
        for l in lines:
            l = l.strip(f' -')
            self.assertIn(l, tree)

    def test_comment(self):
        self.task1.add_comment("This is a comment")
        root_tree = self.root.get_tree()
        print(f'Root Tree:\n{root_tree}')
        self.assertIn("This is a comment",root_tree)


    def test_subtasks_complete(self):
        self.subtask11.complete()
        self.subtask12.complete()
        self.subtask13.complete()
        self.task3.complete()
        self.task4.complete()
        self.subtask21.complete()

        tree = self.root.get_tree()
        print(f'- Task tree:\n{tree}')

        self.assertTrue(self.root.recursively_complete())

if __name__ == '__main__':
    TestTask.execute_all()
