def extract_between_keywords(input_string, start_keyword, end_keyword):
    try:
        start_index = input_string.index(start_keyword) + len(start_keyword)
        end_index = input_string.index(end_keyword)
        return input_string[start_index:end_index].strip()
    except ValueError:
        return ""
