from __future__ import annotations
# ----------------------------------------------



def get_salvaged_json(broken_json: str) -> str:
    control_char_map = {
        '\n': '\\n',
        '\t': '\\t',
        '\r': '\\r',
        '\b': '\\b',
        '\f': '\\f',
        '\\': '\\\\'
    }

    escaped = []
    inside_field = False
    char_is_escaped = False

    for char in broken_json:
        new_char = char

        if char == '"' and not char_is_escaped:
            inside_field = not inside_field

        if inside_field and not char_is_escaped:
            new_char = control_char_map[char] if char in control_char_map else char

        char_is_escaped = char == '\\' and not char_is_escaped
        escaped.append(new_char)

    return ''.join(escaped)