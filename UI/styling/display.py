class Display(str):
    def __new__(cls, value):
        return str.__new__(cls, value)

    @classmethod
    def BLOCK(cls):
        return cls("block")

    @classmethod
    def INLINE(cls):
        return cls("inline")

    @classmethod
    def INLINE_BLOCK(cls):
        return cls("inline-block")

    @classmethod
    def FLEX(cls):
        return cls("flex")

    @classmethod
    def GRID(cls):
        return cls("grid")

    @classmethod
    def NONE(cls):
        return cls("none")

    @classmethod
    def TABLE(cls):
        return cls("table")

    @classmethod
    def TABLE_ROW(cls):
        return cls("table-row")

    @classmethod
    def TABLE_CELL(cls):
        return cls("table-cell")

    @classmethod
    def LIST_ITEM(cls):
        return cls("list-item")
