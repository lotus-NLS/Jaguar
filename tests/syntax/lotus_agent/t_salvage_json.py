import unittest
import json

def get_salvaged_json(broken_json : str) -> str:
    currently_inside_quotes = False
    next_char_escaped = False
    escaped = []

    control_char_map = {
        '\n': '\\n',
        '\t': '\\t',
        '\r': '\\r',
        '\b': '\\b',
        '\f': '\\f',
        '\\': '\\\\'
    }

    for char in broken_json:
        if char == '"' and not next_char_escaped:
            currently_inside_quotes = not currently_inside_quotes

        if currently_inside_quotes and not next_char_escaped:
            if char in control_char_map:
                escaped.append(control_char_map[char])
                continue

        if char == '\\':
            next_char_escaped = True
        else:
            next_char_escaped = False

        escaped.append(char)

    return ''.join(escaped)


class TestSalvageJSON(unittest.TestCase):

    def test_single_newline(self):
        broken_str = '{"key": "value with a new\nline"}'
        repaired_str = get_salvaged_json(broken_str)
        try:
            parsed_json = json.loads(repaired_str)
            self.assertEqual(parsed_json['key'], "value with a new\\nline")
        except json.JSONDecodeError:
            self.fail("Failed to parse repaired JSON")

    def test_tab_and_backslash(self):
        broken_str = '{"key": "value with a tab\\t and a \\\\backslash"}'
        repaired_str = get_salvaged_json(broken_str)
        try:
            parsed_json = json.loads(repaired_str)
            self.assertEqual(parsed_json['key'], "value with a tab\\\\t and a \\\\\\\\backslash")
        except json.JSONDecodeError:
            self.fail("Failed to parse repaired JSON")

    def test_multiple_control_characters(self):
        broken_str = '{"key": "new\nline and\ttab"}'
        repaired_str = get_salvaged_json(broken_str)
        try:
            parsed_json = json.loads(repaired_str)
            self.assertEqual(parsed_json['key'], "new\\nline and\\ttab")
        except json.JSONDecodeError:
            self.fail("Failed to parse repaired JSON")

    def test_no_control_characters(self):
        valid_str = '{"key": "value"}'
        repaired_str = get_salvaged_json(valid_str)
        try:
            parsed_json = json.loads(repaired_str)
            self.assertEqual(parsed_json['key'], "value")
        except json.JSONDecodeError:
            self.fail("Failed to parse repaired JSON")


if __name__ == "__main__":
    unittest.main()
