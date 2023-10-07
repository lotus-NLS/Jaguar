import tiktoken
from tiktoken import Encoding




def num_tokens_from_functions(functions: list[dict], model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of functions."""
    try:
        encoding : Encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    for function in functions:
        function_tokens = get_function_base_tokens(encoding, function)

        if 'parameters' in function:
            parameters = function['parameters']
            if 'properties' in parameters:
                function_tokens += handle_parameters(encoding, parameters)

        num_tokens += function_tokens

    num_tokens += 12
    return num_tokens


def get_function_base_tokens(encoding, function):
    function_tokens = len(encoding.encode(function['name']))
    function_tokens += len(encoding.encode(function['description']))
    return function_tokens


def handle_parameters(encoding : Encoding, parameters : dict):
    function_tokens = 0
    for propertiesKey in parameters['properties']:
        function_tokens += len(encoding.encode(propertiesKey))
        v = parameters['properties'][propertiesKey]
        function_tokens += handle_fields(encoding, v)
    function_tokens += 11
    return function_tokens


def handle_fields(encoding : Encoding, fields_dict : dict):
    function_tokens = 0
    for field, value in fields_dict.items():
        if field == 'type':
            function_tokens += 2
            function_tokens += len(encoding.encode(value))
        elif field == 'description':
            function_tokens += 2
            function_tokens += len(encoding.encode(value))
        elif field == 'enum':
            for o in value:
                function_tokens += 3
                function_tokens += len(encoding.encode(o))
            function_tokens -= 3  # Adjust for the initial extra tokens
        else:
            print(f"Warning: not supported field {field}")
    return function_tokens

