from src.l2_lotus_core.m1_protocol.objective import Objective  # Replace 'your_module' with the actual module name
import unittest

# How do tests work?
# -> All methods starting with "test_" are collected automatically into a test suite
# -> Before each test "setUp" is run and "tearDown" is run after
# -> The success of each test is determined by passing assertion methods provided by the unittest.TestCase class

# ----------------------------------------------------
#

class ObjectiveTester(unittest.TestCase):

    def setUp(self):
        self.root = Objective.make_root("root")
        self.sub = self.root.make_subelement(name='sub')


        print("\n//--------------------------------//")
        print(f"TEST: {self._testMethodName}")
        print(f"Before test, root objective: \n"
              f"{self.root}")

    def tearDown(self):
        print(f"After test, root objective: \n"
              f"{self.root}")

    def test_make_root(self):
        self.assertIsNotNone(self.root)
        self.assertEqual(self.root.desc, "root")
        self.assertIsNotNone(self.root.descendant_dict)

    def test_get_objective(self):
        retrieved_sub = self.root.get_objective(objective_key=self.sub.get_key())
        self.assertEqual(self.sub, retrieved_sub)

    def test_edit(self):
        self.root.edit("new_game")
        self.assertEqual(self.root.desc, "new_game")

    def test_mark_complete(self):
        self.sub.mark_complete()
        self.assertTrue(self.sub.get_is_done())

    def test_cancel(self):
        self.sub.cancel()
        self.assertIsNone(self.root.get_objective(self.sub))

    def test_make_subelement(self):
        sub = self.root.make_subelement("sub2")
        self.assertIsNotNone(sub)
        self.assertEqual(sub.parent, self.root)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ObjectiveTester)
    unittest.TextTestRunner(verbosity=5).run(suite)
