from flask import Flask
from pywebdev.devkit import PyWebApp

# ----------------------------------------------

class ChatHTML(PyWebApp):
    def add_body_content(self):
        with self.add_tag('div', id='chat-window', style='height:300px; border:1px solid #ccc; overflow:auto;'):
            self.text('<!-- Chat history will go here -->')

        self.add_input(input_type='text', the_id='text_bar')
        self.add_input(input_type='button', the_id='Send', value='Send')
        self.add_python_script(rel_path='scripts/simple_script.py')



if __name__ == '__main__':
    app = ChatHTML(title='This new app')
    app.run(debug=True)


