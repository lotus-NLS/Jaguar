from typing import Callable, List
import inspect
from a_globals.method_lib import extract_between_keywords

# ------------------------------------------------

class Toolbox:
    tool_list = []
    
    class Arg:
        def __init__(self, name: str):
            self.name = name

        def get_start_keyword(self):
            return f"START_{self.name.lower()}|"

        def get_end_keyword(self):
            return f"|END_{self.name.lower()}*"

        def extract_value(self, arg_string: str):
            return extract_between_keywords(arg_string, self.get_start_keyword(), self.get_end_keyword())
    
    # ASSUMPTIONS:
    # function : Callable; only keword arguments, only string arguments; apt-description
    class Tool:
        def __init__(self, function: Callable, name: str, description: str):
            self.function = function
            self.name = name

            arg_list = list(inspect.signature(function).parameters.keys())
            self.args = [Toolbox.Arg(arg_name) for arg_name in arg_list]
            self.description = description

            Toolbox.tool_list.append(self)

        def get_tool_info(self):
            tool_description = f'{self.name}: {self.description} To use it, follow the following format:'
            tool_description += f'{self.get_start_keyword()}'

            for tool_arg in self.args:
                tool_description += f"{tool_arg.get_start_keyword()}[arg_value]{tool_arg.get_end_keyword()}"

            tool_description += f'{self.get_end_keyword()}'

            return tool_description

        def handle_call(self, arg_string: str):
            kwargs = {}
            for tool_arg in self.args:
                arg_val = tool_arg.extract_value(arg_string)
                if arg_val is not None:
                    kwargs[tool_arg.name] = arg_val.strip()
                else:
                    print(f"[Warning] Missing argument {tool_arg.name} for tool {self.name}")
                    return None  # If any argument is missing, don't call the function

            result = self.function(**kwargs)
            return result

        def get_start_keyword(self):
            return f'{self.name.upper()}|'

        def get_end_keyword(self):
            return f'|{self.name.upper()}'



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

# if __name__ == "__main__":
#     read_tool = Tools.read
#     write_tool = Tools.write
#
#     print("Read Tool Arguments:")
#     for arg in read_tool.args:
#         print(arg.name)
#
#     print("Read Tool Info:")
#     print(read_tool.get_tool_info())
#
#     print("Write Tool Arguments:")
#     for arg in write_tool.args:
#         print(arg.name)
#
#     print("Write Tool Info:")
#     print(write_tool.get_tool_info())
#
#     # Write to a file using 'write_tool'
#     path_to_file = os.path.expanduser("~/pyWriter/test.txt")
#     content_to_write = "Hello, World!"
#     write_tool_arg_string = f"START_PATH|\n{path_to_file}\n|END_PATH\nSTART_CONTENT|\n{content_to_write}\n|END_CONTENT"
#     write_tool.handle_call(write_tool_arg_string)
#
#     # Read from the same file using 'read_tool'
#     read_tool_arg_string = f"START_PATH|\n{path_to_file}\n|END_PATH"
#     print(read_tool.handle_call(read_tool_arg_string))