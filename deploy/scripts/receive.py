from browser import window, document
from api import Entry, Ends, Flag
from lib import ParagraphConverter

# ----------------------------------------------

chat_window = document["chat-window"]


def make_new_entry(entry : Entry):
    paragraph_converter.add_markdown(markdown_text=f"{entry.get_name()}: {entry.get_content()}")
    new_element = document.createElement("div")
    new_element.innerHTML = paragraph_converter.get()


def handle_engine_data(msg : dict):
    entry_content : str = msg['data']
    new_entry : Entry = Entry.from_serialized_str(s=entry_content)
    window.console.log(f'Agent entry arrived with content: {new_entry.get_content().__repr__()}')

    try:
        last_element = chat_window.children[-1]
    except:
        last_element = None

    if new_entry.flags.get(Flag.IS_ENTRY_START) or last_element is None:
        paragraph_converter.reset()
        make_new_entry(entry=new_entry)
    else:
        paragraph_converter.add_markdown(markdown_text=new_entry.get_content())
        last_element.innerHTML = paragraph_converter.get()


paragraph_converter = ParagraphConverter()
evt_source = window.EventSource.new(f'/{Ends.engine_data.identifier}')
evt_source.onmessage = handle_engine_data
