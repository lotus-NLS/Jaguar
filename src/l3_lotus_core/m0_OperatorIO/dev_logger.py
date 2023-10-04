import time
import traceback

# ---------------------------------------------------------


start_time = time.time()

def get_exception_msg(text: str):
    return (f'[Error]: {text}\n'
            f'{traceback.format_exc()}')

def log_time_after_done(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"""[Debug]: Completed "{get_fully_qualified_name(func)}"; Uptime: {elapsed_time:.2f} seconds""")

    return wrapper


def get_fully_qualified_name(func):
    try:
        return func.__qualname__
    except:
        return f"{func.__name__}"
