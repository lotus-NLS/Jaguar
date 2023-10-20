import time
import traceback

# ---------------------------------------------------------


start_time = time.time()

def get_exception_msg(text: str):
    return (f'[Error]: {text}\n'
            f'{traceback.format_exc()}')

def logging_wrapper(func : callable):
    def get_fully_qualified_name(inner_func):
        try:
            return inner_func.__qualname__
        except:
            return f"{inner_func.__name__}"

    def print_heading(message):
        num_stars = 3  # Number of stars on each side
        print('*' * num_stars + ' ' + message + ' ' + '*' * num_stars)

    def wrapper(*args, **kwargs):
        print_heading(message=f'[Engine update]: Started {get_fully_qualified_name(func)}')
        func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"""[Debug]: Completed "{get_fully_qualified_name(func)}"; Uptime: {elapsed_time:.2f} seconds""")
        print()

    return wrapper


