
class TestModule:
    def __init__(self):
        pass

    @staticmethod
    def test(func : callable):
        def wrapped_func(*args,**kwargs):
            print(f'--- Starting test {func.__name__} ---')
            func(*args,**kwargs)
            print(f'--- Completed test {func.__name__} ---')

        return wrapped_func