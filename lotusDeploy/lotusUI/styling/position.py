class Position(str):
    def __new__(cls, value):
        return str.__new__(cls, value)

    @classmethod
    def STATIC(cls):
        return cls("static")

    @classmethod
    def RELATIVE(cls):
        return cls("relative")

    @classmethod
    def ABSOLUTE(cls):
        return cls("absolute")

    @classmethod
    def FIXED(cls):
        return cls("fixed")

    @classmethod
    def STICKY(cls):
        return cls("sticky")
