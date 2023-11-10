from browser import window, document
from api import Entry, Ends, Flag

# ----------------------------------------------

chat_window = document["chat-window"]

def convert_markdown_to_html(markdown_text):
    converter = window.showdown.Converter.new()
    html = converter.makeHtml(markdown_text)
    return html


def make_new_entry(entry : Entry):
    msg = entry.get_content()
    new_element = document.createElement("div")
    new_element.innerHTML = f"{entry.get_name()}: {msg}"
    chat_window.appendChild(new_element)



def handle_engine_data(msg : dict):
    entry_content : str = msg['data']
    new_entry : Entry = Entry.from_serialized_str(s=entry_content)
    window.console.log(f'Agent entry arrived with content: {new_entry.get_content()}')

    try:
        last_element = chat_window.children[-1]
    except:
        last_element = None

    if new_entry.flags.get(Flag.IS_ENTRY_START) or last_element is None:
        make_new_entry(entry=new_entry)
    else:
        last_element.innerHTML += f"{new_entry.get_content()}"

evt_source = window.EventSource.new(f'/{Ends.engine_data.identifier}')
evt_source.onmessage = handle_engine_data
