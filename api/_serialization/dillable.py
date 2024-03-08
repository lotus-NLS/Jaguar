import dill
from abc import ABC


class Dillable(ABC):
    def to_str(self) -> str:
        return dill.dumps(self).hex()

    @classmethod
    def from_str(cls, dill_str: str):
        return dill.loads(bytes.fromhex(dill_str))
