class Percentage(str):
    def __new__(cls, percentage: int):
        if not (0 <= percentage <= 100):
            print("Warning: Percentage should be between 0 and 100.")
        return str.__new__(cls, f"{percentage}%")


class Pixels(str):
    def __new__(cls, num_pixels: int):
        return str.__new__(cls, f"{num_pixels}px")

