from browser import window, document, ajax
from api import APIMessage, Entry, DialogueRole, Ends, DefaultNetwork
# ----------------------------------------------


def on_complete(req):
    if req.status == 200 or req.status == 0:
        print("Message sent successfully")
    else:
        print("Error sending message")


def send_entry_to_server(msg : str):
    the_entry = Entry(msg=msg,role=DialogueRole.user_role())
    the_api_msg = APIMessage(entry=the_entry)
    window.console.log('I sent the msg :)')

    request_data = {"msg_content": the_api_msg.to_str()}
    request = ajax.Ajax()
    request.bind('complete', on_complete)
    endpoint = Ends.user_data
    request.open(method=endpoint.req_type,
                 url=f'http://{DefaultNetwork.ip}:{DefaultNetwork.port}/{endpoint.name}',
                 param=True)

    request.set_header('content-type', 'application/x-www-form-urlencoded')
    request.send(request_data)


# def append_to_chat(msg : str):
#     chat_window = document["chat-window"]
#     new_element = document.createElement("div")
#     new_element.innerHTML = f"<p>User: {msg}</p>"
#     chat_window.appendChild(new_element)


def handle_user_msg(event):
    _ = event
    text_bar = document["text_bar"]
    entered_text = text_bar.value
    send_entry_to_server(msg=entered_text)
    text_bar.value = ''


def handle_keyup(event):
    if event.key == "Enter":
        handle_user_msg(event)

document["text_bar"].bind("keyup", handle_keyup)
document["Send"].bind("click", handle_user_msg)