from browser import window, document, ajax
from api import APIMessage, Entry, DialogueRole, Ends, DefaultNetwork
import json
# ----------------------------------------------

def handle_user_msg(event):
    _ = event
    entered_text = text_bar.value
    text_bar.value = ''
    append_user_msg(msg=entered_text)

    api_msg = APIMessage(entry=Entry(msg=entered_text,role=DialogueRole.user_role(), is_final=True))
    send_api_msg(api_message=api_msg)


def append_user_msg(msg : str):
    new_element = document.createElement("div")
    new_element.innerHTML = f"<p>User: {msg}</p>"
    chat_window.appendChild(new_element)


def on_complete(req):
    if req.status == 200 or req.status == 0:
        print("Message sent successfully")
    else:
        print("Error sending message")


def send_api_msg(api_message : APIMessage):
    request_data = json.dumps({"msg_content": api_message.to_str()})
    request = ajax.Ajax()
    request.bind('complete', on_complete)
    endpoint = Ends.user_data
    request.open(endpoint.get_req_type(),
                 f'http://{DefaultNetwork.ip}:{DefaultNetwork.port}/{endpoint.identifier}',
                 True)

    request.set_header('content-type', 'application/json')
    request.send(request_data)

    window.console.log('I sent the msg :)')

def handle_keyup(event):
    if event.key == "Enter":
        handle_user_msg(event)

# ----------------------------------------------

chat_window = document["chat-window"]
text_bar = document["text_bar"]
document["text_bar"].bind("keyup", handle_keyup)
document["Send"].bind("click", handle_user_msg)