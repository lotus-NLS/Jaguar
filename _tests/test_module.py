



class TestModule:
    def __init__(self):
        pass


    def log(self, to_log : str):
        pass

    def test(self, func : callable):
        def wrapped_func(*args,**kwargs):
            self.log(f'--- Starting test {func.__name__} ---')
            func(*args,**kwargs)
            self.log(f'--- Completed test {func.__name__} ---\n')

        return wrapped_func