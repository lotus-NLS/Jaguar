import unittest
import json
from src.l2_lotus_agent.m2_action.action import Action


# ---------------------------------------------------------

get_salvaged_json = Action.get_salvaged_json

class TestSalvageJSON(unittest.TestCase):

    def test_no_control_characters(self):
        valid_str = '{"key": "value"}'
        repaired_str = get_salvaged_json(valid_str)
        try:
            parsed_json = json.loads(repaired_str)
            self.assertEqual(parsed_json['key'], "value")
        except json.JSONDecodeError:
            self.fail("Failed to parse repaired JSON")

    def test_single_newline(self):
        broken_str = '{"key": "value with a new\nline"}'
        repaired_str = get_salvaged_json(broken_str)
        try:
            parsed_json = json.loads(repaired_str)
            self.assertEqual(parsed_json['key'], "value with a new\nline")
        except json.JSONDecodeError:
            self.fail("Failed to parse repaired JSON")

    def test_tab_and_backslash(self):
        broken_str = '{"key": "value with a tab\t"}'
        repaired_str = get_salvaged_json(broken_str)
        try:
            parsed_json = json.loads(repaired_str)
            self.assertEqual(parsed_json['key'], "value with a tab\t")
        except json.JSONDecodeError:
            self.fail("Failed to parse repaired JSON")

    def test_multiple_control_characters(self):
        broken_str = '{"key": "new\nline and\ttab"}'
        repaired_str = get_salvaged_json(broken_str)
        try:
            parsed_json = json.loads(repaired_str)
            self.assertEqual(parsed_json['key'], "new\nline and\ttab")
        except json.JSONDecodeError:
            self.fail("Failed to parse repaired JSON")



if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSalvageJSON)
    unittest.TextTestRunner(verbosity=5).run(suite)

