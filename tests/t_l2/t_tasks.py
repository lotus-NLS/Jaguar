import unittest

from engine.l1_agents.protocol.stepinfo import Objective
from holytools.devtools import Unittest


class TestTask(Unittest):
    def setUp(self):
        self.root = Objective("Main Task", is_root=True)
        self.task1 = self.root.add_subtask("Task 1")
        self.task2 = self.root.add_subtask("Task 2")
        self.task3 = self.root.add_subtask("Task 3")
        self.task4 = self.root.add_subtask("Task 4")
        self.subtask1 = self.task1.add_subtask("Subtask 1.1")
        self.subtask2 = self.task1.add_subtask("Subtask 1.2")
        self.subtask3 = self.task1.add_subtask("Subtask 1.3")

        self.task1.complete()
        self.task4.complete()

    def test_get_Tree(self):
        print(self.root.get_tree())

    def test_get_by_id(self):
        print(self.root.get_descendant('11').content)

if __name__ == '__main__':
    TestTask.execute_all()


