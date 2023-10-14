from typing import Optional
from tiktoken import Encoding
from src.l3_lotus_core import Entry

# ---------------------------------------------------------

class Tokenizer:
    def __init__(self, encoding : Encoding, tokens_per_msg : int = 3, tokens_per_name : int = 1):
        self.encoding : encoding = encoding
        self.encode = encoding.encode
        self.decode = encoding.decode
        self.base_tokens_per_entry = tokens_per_msg
        self.tokens_per_name = tokens_per_name


    def get_context_tokens(self, entries : list[Entry], funct_docs : Optional[list[dict]] = None):
        # Every reply is primed with <|start|>assistant<|message|>
        num_tokens = 3
        num_tokens += sum([self.get_entry_tokens(entry=entry) for entry in entries])
        if not funct_docs is None:
            num_tokens += self.get_funct_docs_tokens(funct_doc_list=funct_docs)
        return num_tokens


    def get_entry_tokens(self, entry : Entry):
        num_tokens = self.base_tokens_per_entry
        for key, content in entry.items():
            num_tokens += self.get_string_tokens(the_str=content)
            if key == "name":
                num_tokens += self.tokens_per_name
        return num_tokens


    def get_string_tokens(self, the_str : str) -> int:
        return len(self.encode(the_str))


    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        encoded_str = self.encode(the_str)
        return self.decode(encoded_str[:max_tokens])


    def get_funct_docs_tokens(self, funct_doc_list: list[dict]) -> int:
        num_tokens = 0
        for funct_doc in funct_doc_list:
            function_tokens = self._get_funct_header_tokens(funct_json_doc=funct_doc)
            function_tokens += self._get_funct_args_tokens(funct_json_doc=funct_doc)
            num_tokens += function_tokens
        num_tokens += 12

        return num_tokens

    # ---------------------------------------------------------
    # Utils

    def _get_funct_header_tokens(self, funct_json_doc : dict) -> int:
        function_tokens = len(self.encode(funct_json_doc['name']))
        function_tokens += len(self.encode(funct_json_doc['description']))
        return function_tokens


    def _get_funct_args_tokens(self, funct_json_doc : dict) -> int:
        param_tokens = 0
        try:
            arg_docs_dict = funct_json_doc['parameters']['properties']
            for arg_name in arg_docs_dict:
                param_tokens += self._get_arg_tokens(arg_name=arg_name, arg_json_doc=arg_docs_dict[arg_name])
            param_tokens += 11
        except:
            pass

        return param_tokens


    def _get_arg_tokens(self, arg_name : str, arg_json_doc: dict) -> int:
        arg_tokens = self.get_string_tokens(the_str=f'{arg_name}')
        for field, value in arg_json_doc.items():
            if field == 'type':
                arg_tokens += 2
                arg_tokens += len(self.encode(value))
            elif field == 'description':
                arg_tokens += 2
                arg_tokens += len(self.encode(value))
            elif field == 'enum':
                sum([3 + len(self.encode(x)) for x in value])
                arg_tokens -= 3
            else:
                print(f"[Debug]: Warning: Unsupported field {field}")

        return arg_tokens
