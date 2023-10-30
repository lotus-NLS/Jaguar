from flask import Flask
from yattag import Doc

# ----------------------------------------------


brython_script_content = """
from browser import document

def append_message(event):
    chat_window = document["chat-window"]
    text_bar = document["text_bar"]
    new_element = document.createElement("div")
    new_element.innerHTML = f"<p>User: {text_bar.value}</p>"
    chat_window.appendChild(new_element)
    text_bar.value = ""

document["Send"].bind("click", append_message)
"""


class DocumentWriter:
    def __init__(self):
        self.doc, self.tag, self.text = Doc().tagtext()

    def add_script(self, script_type, content):
        with self.add_tag('script', type=script_type):
            self.add_plain_text(content)

    def add_plain_text(self, text):
        self.doc.asis(text)

    def add_tag(self, tag_name, *args, **kwargs):
        return self.tag(tag_name, *args, **kwargs)

    def add_stag(self, tag_name, **attributes):
        self.doc.stag(tag_name, **attributes)

    def get_value(self) -> str:
        return self.doc.getvalue()

    # ----------------------------------------------

    def get_index(self) -> str:
        with self.add_tag('html', lang='en'):
            self.get_head()
            self.get_body()
        return self.get_value()


    def get_head(self):
        with self.add_tag('head'):
            self.add_plain_text('<meta charset="UTF-8">')
            with self.add_tag('title'):
                self.text('Flask & Brython Chat')
            self.add_plain_text('<script src="https://cdn.jsdelivr.net/npm/brython@3.11/brython.min.js"></script>')

    def get_body(self):
        with self.add_tag('body', onload="brython()"):
            with self.add_tag('div', id='chat-window', style='height:300px; border:1px solid #ccc; overflow:auto;'):
                self.text('<!-- Chat history will go here -->')
            self.add_stag('input', type='text', id='text_bar')
            self.add_stag('input', type='button', id='Send', value='Send')
            self.add_script('text/python', brython_script_content)

# ----------------------------------------------


app = Flask(__name__)

@app.route('/')
def route_index():
    writer = DocumentWriter()
    return writer.get_index()

if __name__ == '__main__':
    app.run(debug=True)


