import math

class Calculator:
    @staticmethod
    def add(x, y):
        return x + y

    @staticmethod
    def subtract(x, y):
        return x - y

    @staticmethod
    def multiply(x, y):
        return x * y

    @staticmethod
    def divide(x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero.")
        return x / y

    @staticmethod
    def exp(x, y):
        return x ** y


    @staticmethod
    def f(x):
        return x**2 + 2*x + 1

    @staticmethod
    def g(x):
        if x == 1:
            return 3  # Returning the limit of g(x) as x approaches 1
        return (x**3 - 1) / (x - 1)

    @staticmethod
    def log(x, base=math.e):
        if x <= 0:
            raise ValueError("Logarithm undefined for non-positive values.")
        return math.log(x, base)
