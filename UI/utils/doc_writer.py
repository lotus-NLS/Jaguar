from yattag import Doc
from abc import abstractmethod

# ----------------------------------------------


class DocWriter:
    def __init__(self, title: str):
        self.doc, self.tag, self.text = Doc().tagtext()
        self.title = title

    # ----------------------------------------------

    def get_index(self) -> str:
        with self.add_tag('html', lang='en'):
            with self.add_tag('head'):
                self.add_head_content()
            with self.add_tag('body', onload="brython()"):
                self.add_body_content()
        return self.get_value()

    # ----------------------------------------------
    # Head

    def add_head_content(self):
        self.add_charset()
        self.add_title()
        self.add_plain_text('<script src="https://cdn.jsdelivr.net/npm/brython@3.11/brython.min.js"></script>')

    def add_charset(self, charset="UTF-8"):
        self.add_plain_text(f'<meta charset="{charset}">')

    def add_title(self):
        with self.add_tag('title'):
            self.text(f'{self.title}')

    # ----------------------------------------------
    # Body

    @abstractmethod
    def add_body_content(self):
        pass

    # ----------------------------------------------

    def add_input(self, input_type, id_name, **kwargs):
        self.add_stag('input', type=input_type, id=id_name, **kwargs)

    def add_python_script(self, content):
        self.add_script('text/python', content)

    def add_script(self, script_type, content):
        with self.add_tag('script', type=script_type):
            self.add_plain_text(text=content)

    def add_plain_text(self, text):
        self.doc.asis(text)

    def add_tag(self, tag_name, *args, **kwargs):
        return self.tag(tag_name, *args, **kwargs)

    def add_stag(self, tag_name, **attributes):
        self.doc.stag(tag_name, **attributes)

    def get_value(self) -> str:
        return self.doc.getvalue()

