from pywebdev import PyWebApp

# ----------------------------------------------

class LotusWebApp(PyWebApp):
    def add_body_content(self):
        chat_window_style = 'height:80vh; width:80%; border:1px solid #ccc; overflow:auto; margin:auto;'
        with self.add_tag('div', id='chat-window', style=chat_window_style):
            self.generate_text('')

        # Container for Text and Send button
        container_style = 'display:flex; justify-content:center; width:100%;'
        with self.add_tag('div', style=container_style):
            # Text field
            text_field_style = 'width:80%; margin:10px;'
            self.add_text_field(the_id='text_bar', style=text_field_style)

            # Send button
            send_button_style = 'margin:10px;'
            self.add_button(the_id='Send', value='Send', style=send_button_style)

        # Chat Interactivity
        self.add_python_script(relPath='deploy/interaction/do_chat.py')

