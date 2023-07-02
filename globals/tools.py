from typing import Callable, List
from method_lib import *
import inspect

class Arg:
    def __init__(self, name: str):
        self.name = name

    def get_start_keyword(self):
        return f"--START_{self.name.upper()}|"

    def get_end_keyword(self):
        return f"|--END_{self.name.upper()}"

    def extract_value(self, arg_string: str):
        return extract_between_keywords(arg_string, self.get_start_keyword(), self.get_end_keyword())


# Contract specifications
# ASSUMPTIONS:
# function : Callable; only keword arguments, only string arguments; apt-description

# ASSURANCES
# tool : can provide 

class Tool:
    def __init__(self, function: Callable, name: str, description: str):
        self.function = function
        self.name = name
        arg_list = list(inspect.signature(function).parameters.keys())
        self.args = [Arg(arg_name) for arg_name in arg_list]
        self.description = description

    def get_tool_info(self):
        tool_description = f"{self.name}: {self.description} To use it, follow this format: "

        for arg in self.args:
            arg_description = f"{arg.get_start_keyword()}[arg_value]{arg.get_end_keyword()}"
            tool_description += arg_description

        usage_instruction = f"{self.get_start_keyword()}{tool_description}{self.get_end_keyword()}"

        return usage_instruction

    def handle_call(self, arg_string: str):
        kwargs = {}
        for arg in self.args:
            arg_val = arg.extract_value(arg_string)
            if arg_val is not None:
                kwargs[arg.name] = arg_val.strip()
            else:
                print(f"[Warning] Missing argument {arg.name} for tool {self.name}")
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

agent_toolbox =  [Tools.read, Tools.write]

# -----------------------------------

if __name__ == "__main__":
    read_tool = Tools.read
    write_tool = Tools.write

    print("Read Tool Arguments:")
    for arg in read_tool.args:
        print(arg.name)

    print("Read Tool Info:")
    print(read_tool.get_tool_info())

    print("Write Tool Arguments:")
    for arg in write_tool.args:
        print(arg.name)

    print("Write Tool Info:")
    print(write_tool.get_tool_info())
