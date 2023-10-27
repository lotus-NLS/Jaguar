class Cursor(str):
    def __new__(cls, value):
        return str.__new__(cls, value)

    @classmethod
    def DEFAULT(cls):
        return cls("default")

    @classmethod
    def POINTER(cls):
        return cls("pointer")

    @classmethod
    def WAIT(cls):
        return cls("wait")

    @classmethod
    def TEXT(cls):
        return cls("text")

    @classmethod
    def CROSSHAIR(cls):
        return cls("crosshair")

    @classmethod
    def MOVE(cls):
        return cls("move")

    @classmethod
    def NOT_ALLOWED(cls):
        return cls("not-allowed")

    @classmethod
    def GRAB(cls):
        return cls("grab")

    @classmethod
    def GRABBING(cls):
        return cls("grabbing")