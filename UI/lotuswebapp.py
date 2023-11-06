import os
from pywebdev.devkit import PyWebApp



# ----------------------------------------------

class LotusWebApp(PyWebApp):
    def add_body_content(self):
        # Chat window
        # chat_window_style = Style(height='300px', border='1px solid #ccc', overflow='auto')
        # self.add_tag(tag_name='div', id='chat-window', style=chat_window_style)
        with self.add_tag('div', id='chat-window', style='height:300px; border:1px solid #ccc; overflow:auto;'):
            self.generate_text('')

        # Text and send button
        self.add_text_field(the_id='text_bar')
        self.add_button(the_id='Send', value ='Send')

        # Chat Interactivity
        self.add_python_script(relPath='scripts/send.py')
        self.add_python_script(relPath='scripts/receive.py')
