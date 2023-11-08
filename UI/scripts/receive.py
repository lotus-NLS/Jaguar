from browser import window, document
from api import Entry, Ends

# ----------------------------------------------

chat_window = document["chat-window"]

def make_new_entry(msg):
    new_element = document.createElement("div")
    new_element.innerHTML = f"\n<p>Agent: {msg}</p>"
    chat_window.appendChild(new_element)

def handle_agent_msg(msg : dict):

    # window.console.log(entry_msg['data'])

    content : str = msg['data']


    new_entry : Entry = Entry.from_str(s=content)
    is_entry_end = new_entry.flags.is_entry_end
    msg = new_entry.get_content()
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


evt_source = window.EventSource.new(f'/{Ends.agent_data.identifier}')
evt_source.bind('customEventName', handle_agent_msg)
