from typing import Callable, List
from method_lib import *
import inspect



class Tool:
    def __init__(self, function: Callable, name: str, description: str):
        self.function = function
        self.name = name
        self.args = list(inspect.signature(function).parameters.keys())
        self.description = description

    def handle_call(self, arg_string: str):
        kwargs = {}
        for arg in self.args:
            keyword = f"--START_{arg.upper()}|"
            end_keyword = f"|--END_{arg.upper()}"
            arg_val = extract_between_keywords(arg_string, keyword, end_keyword)
            if arg_val is not None:
                kwargs[arg] = arg_val.strip()
            else:
                print(f"[Warning] Missing argument {arg} for tool {self.name}")
                return None  # If any argument is missing, don't call the function

        # Call the function associated with the tool with the parsed arguments
        result = self.function(**kwargs)
        return result

    def get_start_keyword(self):
        return f'{self.name.upper()}|'

    def get_end_keyword(self):
        return f'|/{self.name.upper()}'


class Function_lib:
    @staticmethod
    def read_file(path: str):
        with open(path, 'r') as file:
            return file.read()

    @staticmethod
    def write_file(path: str, content: str):
        with open(path, 'w') as file:
            file.write(content)
        return True


class Tools:
    read = Tool(
        function=Function_lib.read_file,
        name="READ",
        description="The 'READ' tool allows you to read the contents of a file. This tool has one argument: 'path', which specifies the path to the file you want to read."
    )

    write = Tool(
        function=Function_lib.write_file,
        name="WRITE",
        description="The 'WRITE' tool allows you to write content to a file. This tool has two arguments: 'path', which specifies the path to the file you want to write to, and 'content', which specifies the content you want to write."
    )


# -----------------------------------
# Code testing
# def main():
#     # Test tools
#     print(f"Read tool args: {Tools.read.args}")
#     print(f"Write tool args: {Tools.write.args}")
#
# if __name__ == "__main__":
#     main()