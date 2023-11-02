from pywebdev.browser import document

def append_message(event):
    _ = event
    chat_window = document["chat-window"]
    text_bar = document["text_bar"]
    new_element = document.createElement("div")
    new_element.innerHTML = f"<p>User: {text_bar.value}</p>"
    chat_window.appendChild(new_element)
    text_bar.value = ""


def handle_keyup(event):
    if event.key == "Enter":
        append_message(event)

document["text_bar"].bind("keyup", handle_keyup)
document["Send"].bind("click", append_message)