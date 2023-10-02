import traceback

def get_exception_msg(text: str):
    return (f'[Error]: {text}\n'
            f'{traceback.format_exc()}')