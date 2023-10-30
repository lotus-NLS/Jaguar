from flask import Flask
from UI.utils.doc_writer import DocWriter

# ----------------------------------------------


simple_script = """
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


class ChatHTML(DocWriter):
    def add_body_content(self):
        with self.add_tag('div', id='chat-window', style='height:300px; border:1px solid #ccc; overflow:auto;'):
            self.text('<!-- Chat history will go here -->')
        self.add_stag('input', type='text', id='text_bar')
        self.add_stag('input', type='button', id='Send', value='Send')
        self.add_python_script(content=simple_script)


app = Flask(__name__)
@app.route('/')
def route_index():
    this_page = ChatHTML(title='This new app')
    return this_page.get_index()


if __name__ == '__main__':
    app.run(debug=True)


