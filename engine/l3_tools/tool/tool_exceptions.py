from func_timeout import FunctionTimedOut

class ToolException(Exception):
    pass


class MissingArgs(ToolException):
    pass

class InvalidArgValue(ToolException):
    pass
