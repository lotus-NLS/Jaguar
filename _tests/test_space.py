import os
import openai
import time



def extract_between_keywords(input_string, start_keyword, end_keyword):
    try:
        start_index = input_string.index(start_keyword) + len(start_keyword)
        end_index = input_string.index(end_keyword)
        return input_string[start_index:end_index]
    except ValueError:
        return ""


# Testing the function
print(extract_between_keywords("\nPATH\n /home/user/documents/file.txt \nEND_PATH\n", "\nPATH\n", "\nEND_PATH\n"))  # Should print "/home/user/documents/file.txt"
print(extract_between_keywords("The quick brown fox jumps over the lazy dog", "quick", "over"))  # Should print "brown fox jumps"
print(extract_between_keywords("No keywords in this string", "start", "end"))  # Should print ""
