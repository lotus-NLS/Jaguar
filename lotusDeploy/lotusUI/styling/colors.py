class Color(str):
    def __new__(cls, value):
        return str.__new__(cls, value)

    @classmethod
    def BLACK(cls):
        return cls("black")

    @classmethod
    def WHITE(cls):
        return cls("white")

    @classmethod
    def BLUE(cls):
        return cls("blue")

    @classmethod
    def LIGHT_BLUE(cls):
        return cls("lightblue")

    @classmethod
    def DARK_BLUE(cls):
        return cls("darkblue")

    @classmethod
    def RED(cls):
        return cls("red")

    @classmethod
    def LIGHT_RED(cls):
        return cls("lightcoral")

    @classmethod
    def DARK_RED(cls):
        return cls("darkred")

    @classmethod
    def GREEN(cls):
        return cls("green")

    @classmethod
    def LIGHT_GREEN(cls):
        return cls("lightgreen")

    @classmethod
    def DARK_GREEN(cls):
        return cls("darkgreen")

    @classmethod
    def YELLOW(cls):
        return cls("yellow")

    @classmethod
    def ORANGE(cls):
        return cls("orange")

    @classmethod
    def PURPLE(cls):
        return cls("purple")

    @classmethod
    def PINK(cls):
        return cls("pink")

    @classmethod
    def BROWN(cls):
        return cls("brown")

    @classmethod
    def GRAY(cls):
        return cls("gray")

    @classmethod
    def LIGHT_GRAY(cls):
        return cls("lightgray")

    @classmethod
    def DARK_GRAY(cls):
        return cls("darkgray")