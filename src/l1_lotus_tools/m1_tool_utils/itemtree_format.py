def is_valid_hierarchy_format(lines: list[str]) -> bool:
    format_correct = True

    if lines[0].startswith('-'):
        format_correct = False

    prev_indent_level = 0

    for line in lines[1:]:
        curr_indent_level = get_leading_dashes_count(line)

        if curr_indent_level > prev_indent_level + 1:
            format_correct = False
            break

        if not curr_indent_level > 0:
            format_correct = False
            break

        prev_indent_level = curr_indent_level

    return format_correct


def get_leading_dashes_count(line: str) -> int:
    count = 0
    for char in line:
        if char == '-':
            count += 1
        else:
            break
    return count