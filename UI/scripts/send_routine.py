from pywebdev.browser import window, document

# ----------------------------------------------

# The socket of the website
socket = window.io.connect('http://localhost:5000')

def send_to_server(msg : str):
    window.console.log('I sent the msg :)')
    socket.emit('message', msg)


# def append_to_chat(msg : str):
#     chat_window = document["chat-window"]
#     new_element = document.createElement("div")
#     new_element.innerHTML = f"<p>User: {msg}</p>"
#     chat_window.appendChild(new_element)


def handle_user_msg(event):
    _ = event
    text_bar = document["text_bar"]
    entered_text = text_bar.value
    send_to_server(msg=entered_text)
    text_bar.value = ''


def handle_keyup(event):
    if event.key == "Enter":
        handle_user_msg(event)

document["text_bar"].bind("keyup", handle_keyup)
document["Send"].bind("click", handle_user_msg)