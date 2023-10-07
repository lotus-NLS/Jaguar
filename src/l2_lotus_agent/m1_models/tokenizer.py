import tiktoken
from tiktoken import Encoding


# ---------------------------------------------------------


class Tokenizer:
    def __init__(self, encoder : Encoding):
        self.encoder : Encoding = encoder

    def num_tokens_from_functions(self, funct_doc_list: list[dict]):
        num_tokens = 0
        for funct_doc in funct_doc_list:
            function_tokens = self.get_funct_header_tokens(funct_json_doc=funct_doc)
            function_tokens += self.get_funct_args_tokens(funct_json_doc=funct_doc)
            num_tokens += function_tokens
        num_tokens += 12

        return num_tokens

    def get_funct_header_tokens(self, funct_json_doc : dict) -> int:
        function_tokens = len(self.encoder.encode(funct_json_doc['name']))
        function_tokens += len(self.encoder.encode(funct_json_doc['description']))
        return function_tokens


    def get_funct_args_tokens(self, funct_json_doc : dict) -> int:
        param_tokens = 0
        try:
            arg_docs_dict = funct_json_doc['parameters']['properties']
            for arg_name in arg_docs_dict:
                param_tokens += self.get_arg_tokens(arg_name=arg_name, arg_json_doc=arg_docs_dict[arg_name])
            param_tokens += 11
        except:
            pass

        return param_tokens

    def get_arg_tokens(self, arg_name : str, arg_json_doc: dict) -> int:

        arg_tokens = len(self.encoder.encode(text=f'{arg_name}'))
        for field, value in arg_json_doc.items():
            if field == 'type':
                arg_tokens += 2
                arg_tokens += len(self.encoder.encode(value))
            elif field == 'description':
                arg_tokens += 2
                arg_tokens += len(self.encoder.encode(value))
            elif field == 'enum':
                sum([3+len(self.encoder.encode(x)) for x in value])
                arg_tokens -= 3
            else:
                print(f"[Debug]: Warning: Unsupported field {field}")

        return arg_tokens
