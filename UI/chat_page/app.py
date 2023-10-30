from flask import Flask
from yattag import Doc

class DocumentWriter:
    def __init__(self):
        self.doc, self.tag, self.text = Doc().tagtext()

    def add_script(self, script_type, content):
        with self.tag('script', type=script_type):
            self.doc.asis(content)

    def get_value(self):
        return self.doc.getvalue()


app = Flask(__name__)

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


@app.route('/')
def index():
    writer = DocumentWriter()

    with writer.tag('html', lang='en'):
        with writer.tag('head'):
            writer.doc.asis('<meta charset="UTF-8">')
            with writer.tag('title'):
                writer.text('Flask & Brython Chat')
            writer.doc.asis('<script src="https://cdn.jsdelivr.net/npm/brython@3.11/brython.min.js"></script>')

        with writer.tag('body', onload="brython()"):
            with writer.tag('div', id='chat-window', style='height:300px; border:1px solid #ccc; overflow:auto;'):
                writer.text('<!-- Chat history will go here -->')
            writer.doc.stag('input', type='text', id='text_bar')
            writer.doc.stag('input', type='button', id='Send', value='Send')

            writer.add_script('text/python', brython_script_content)

    return writer.get_value()


if __name__ == '__main__':
    app.run(debug=True)