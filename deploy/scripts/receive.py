from browser import window, document
from api import Entry, Ends, Flag
from lib import ParagraphConverter

# ----------------------------------------------

class AgentChat:
    def __init__(self):
        self.last_element = None
        self.paragraph_converter = ParagraphConverter()


    def make_new_entry(self,entry : Entry):
        self.paragraph_converter.add_markdown(markdown_text=f"{entry.get_name()}: {entry.get_content()}")
        new_element = document.createElement("div")
        new_element.innerHTML = self.paragraph_converter.get()
        self.last_element = new_element
        chat_window.appendChild(new_element)

    def handle_engine_data(self, msg : dict):
        entry_content : str = msg['data']
        new_entry : Entry = Entry.from_serialized_str(s=entry_content)
        print(f'Agent entry arrived with content: {new_entry.get_content().__repr__()}; Flags: {new_entry.flags.as_text()}')

        if new_entry.flags.get(Flag.IS_ENTRY_START) or self.last_element is None:
            self.paragraph_converter.reset()
            self.make_new_entry(entry=new_entry)
        else:
            self.paragraph_converter.add_markdown(markdown_text=new_entry.get_content())
            self.last_element.innerHTML = self.paragraph_converter.get()


chat_window = document["chat-window"]
agent_chat = AgentChat()
evt_source = window.EventSource.new(f'/{Ends.engine_data.identifier}')
evt_source.onmessage = agent_chat.handle_engine_data
