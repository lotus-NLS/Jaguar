from abc import abstractmethod

class Document(dict):
    @abstractmethod
    def createElement(self):
        pass

document = Document()