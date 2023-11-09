from browser import window, document
from api import Entry, Ends

# ----------------------------------------------

chat_window = document["chat-window"]

def make_new_entry(msg):
    new_element = document.createElement("div")
    new_element.innerHTML = f"<p>{msg}</p>"
    chat_window.appendChild(new_element)


def handle_engine_msg(msg : dict):
    entry_content : str = msg['data']
    new_entry : Entry = Entry.from_serialized_str(s=entry_content)
    is_entry_end = new_entry.flags.is_entry_end
    msg = new_entry.get_content()

    window.console.log(f'Agent entry arrived with content: {msg}')
    # window.console.log(f'{last_element is None}; {is_entry_end}')



    try:
        last_element = chat_window.children[-1]
    except:
        last_element = None

    if is_entry_end or last_element is None:
        make_new_entry(msg=msg)
    else:
        last_element.innerHTML += f"{msg}"


evt_source = window.EventSource.new(f'/{Ends.agent_data.identifier}')
evt_source.bind('customEventName', handle_engine_msg)
