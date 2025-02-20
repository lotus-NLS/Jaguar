from engine.l3_aos.workspaces.taskws import Mandate
from holytools.devtools import Unittest


class TestTask(Unittest):
    def setUp(self):
        self.root = Mandate("Main Task", is_root=True)
        self.task1 = self.root.add_subtask("Task 1")
        self.task2 = self.root.add_subtask("Task 2")
        self.task3 = self.root.add_subtask("Task 3")
        self.task4 = self.root.add_subtask("Task 4")
        self.subtask1 = self.task1.add_subtask("Subtask 1.1")
        self.subtask2 = self.task1.add_subtask("Subtask 1.2")
        self.subtask3 = self.task1.add_subtask("Subtask 1.3")

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
        print(f'Name of task wiith id 1: {self.root.get_descendant("1").name}')
        self.assertEqual(self.root.get_descendant('1').name, self.task1.name)
        self.assertEqual(self.root.get_descendant('11').name, self.subtask1.name)

    def test_complete(self):
        self.root.complete()


    def test_from_yaml_str(self):
        yaml_str = (f'- Task 1\n'
                    f' -Subtask 1.1\n'
                    f'- Task 2')
        root = Mandate.from_yaml(yaml_str)
        tree = root.get_tree()

        lines = yaml_str.split()
        print(f'Yaml generated task tree: \n{tree}')
        for l in lines:
            l = l.strip(f' -')
            self.assertIn(l, tree)


if __name__ == '__main__':
    TestTask.execute_all()


