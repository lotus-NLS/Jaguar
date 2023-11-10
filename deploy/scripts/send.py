from browser import document
from api import APIMessage, Entry, DialogueRole, DefaultNetwork
from lib.client import Client
# ----------------------------------------------

def handle_user_msg(event):
    _ = event
    entered_text = text_bar.value
    text_bar.value = ''
    append_user_msg(msg=entered_text)

    api_msg = APIMessage(entry=Entry(msg=entered_text,role=DialogueRole.user_role(), is_final=True))
    the_client.send_api_msg(api_message=api_msg)

def append_user_msg(msg : str):
    new_element = document.createElement("div")
    new_element.innerHTML = f"<p>User: {msg}</p>"
    chat_window.appendChild(new_element)


def handle_keyup(event):
    if event.key == "Enter":
        handle_user_msg(event)

# ----------------------------------------------
the_client = Client(ip=DefaultNetwork.ip,port=DefaultNetwork.port)
chat_window = document["chat-window"]
text_bar = document["text_bar"]
document["text_bar"].bind("keyup", handle_keyup)
document["Send"].bind("click", handle_user_msg)