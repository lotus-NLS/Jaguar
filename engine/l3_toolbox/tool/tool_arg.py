from typing import Optional


class ToolArg:
    def __init__(self, name : str, dtype : type, desc : str,
                       choices : Optional[list] =  None, is_optional : bool = False):
        self.name : str = name
        self.dtype : type = dtype
        self.desc : str = desc
        self.choices: Optional[list[str]] = choices
        self.is_optional : bool = is_optional

        self.val : Optional = None


    def get_arg_json_doc(self) -> dict[str,str]:
        arg_doc = {
            'type': self.get_json_type(self.dtype),
            'description': f'{self.desc}',
        }

        if not self.choices is None:
            arg_doc['enum'] = self.choices

        return arg_doc

    @staticmethod
    def get_json_type(python_type) -> Optional[str]:
        # The 'array' type corresponding to dict and list, seem to break something on OpenAI end,
        # hence why I didn't include them; See logs (@ https://www.notion.so/pyWrite0-3-a53c1b16ef3646df9c141a144f8197a2)

        default_type = 'string'
        type_mapping = {
            int: "number",
            float: "number",
            str: "string",
            bool: "boolean",
            type(None): "null",
            dict: "object"
        }

        if python_type in type_mapping:
            json_type = type_mapping[python_type]
        else:
            json_type = default_type

        return json_type


    def value_is_valid(self) -> bool:
        if self.choices is None:
            return True

        return self.val in self.choices
