from browser import window, document

# ----------------------------------------------

chat_window = document["chat-window"]

def make_new_entry(msg):
    new_element = document.createElement("div")
    new_element.innerHTML = f"\n<p>Agent: {msg}</p>"
    chat_window.appendChild(new_element)

def handle_agent_msg(msg : str, is_entry_end = True):
    window.console.log('Agent message arrived :)')

    try:
        last_element = chat_window.children[-1]
    except:
        last_element = None

    window.console.log(f'{last_element is None}; {is_entry_end}')

    if is_entry_end or last_element is None:
        make_new_entry(msg=msg)
    else:
        last_element.innerHTML += f"{msg}"


def handle_custom_event(msg):
    window.console.log('asdf')

evt_source = window.EventSource.new('/stream')
evt_source.bind('customEventName', handle_custom_event)
