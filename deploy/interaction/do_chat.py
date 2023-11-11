from browser import document, window

from lib import Chat
from api import Ends

# ----------------------------------------------

the_chat = Chat()

document["text_bar"].bind("keyup", the_chat.handle_keyup)
document["Send"].bind("click", the_chat.handle_user_msg)
evt_source = window.EventSource.new(f'/{Ends.engine_data.identifier}')
evt_source.onmessage = the_chat.handle_engine_data