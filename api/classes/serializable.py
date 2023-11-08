import base64
import pickle

# ----------------------------------------------

class Serializable:

    def __getstate__(self):
        pass

    def to_str(self) -> str:
        return base64.b64encode(pickle.dumps(self)).decode('utf-8')

    @staticmethod
    def from_str(s: str):
        return pickle.loads(base64.b64decode(s.encode('utf-8')))