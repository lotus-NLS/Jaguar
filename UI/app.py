from flask import Flask
from pywebdev.devkit import DocWriter

# ----------------------------------------------

class ChatHTML(DocWriter):
    def add_body_content(self):
        with self.add_tag('div', id='chat-window', style='height:300px; border:1px solid #ccc; overflow:auto;'):
            self.text('<!-- Chat history will go here -->')

        self.add_input(input_type='text', the_id='text_bar')
        self.add_input(input_type='button', the_id='Send', value='Send')
        self.add_python_script(rel_path='scripts/simple_script.py')


app = Flask(__name__)
@app.route('/')
def route_index():
    this_page = ChatHTML(title='This new app')
    return this_page.get_index()


if __name__ == '__main__':
    app.run(debug=True)


