from browser import window, document
from api import Flag
from api import APIMessage, Entry, DialogueRole, DefaultNetwork
from .client import ClientIO
# ----------------------------------------------

class ParagraphConverter:
    def __init__(self):
        self.markdown_content = ""
        self.converter = window.showdown.Converter.new()

    def reset(self):
        self.markdown_content = ""

    def add_markdown(self, markdown_text):
        self.markdown_content += markdown_text + "\n"

    def get(self):
        return self.converter.makeHtml(self.markdown_content)


class Chat:
    def __init__(self):
        self.last_element = None
        self.paragraph_converter = ParagraphConverter()
        self.chat_window = document["chat-window"]
        self.text_bar = document["text_bar"]
        self.client = ClientIO(ip=DefaultNetwork.ip, port=DefaultNetwork.port)

    # ----------------------------------------------
    # handlers

    def handle_keyup(self,event):
        if event.key == "Enter":
            self.handle_user_msg(event)

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


    def handle_user_msg(self,event):
        _ = event
        entered_text = self.text_bar.value
        self.text_bar.value = ''
        self.append_user_msg(msg=entered_text)

        api_msg = APIMessage(entry=Entry(msg=entered_text,role=DialogueRole.user_role(), is_final=True))
        self.client.send_api_msg(api_message=api_msg)

    # ----------------------------------------------
    # actions

    def make_new_entry(self,entry : Entry):
        self.paragraph_converter.add_markdown(markdown_text=f"{entry.get_name()}: {entry.get_content()}")
        new_element = document.createElement("div")
        new_element.innerHTML = self.paragraph_converter.get()
        self.last_element = new_element
        self.chat_window.appendChild(new_element)


    def append_user_msg(self,msg : str):
        paragraph_converter = ParagraphConverter()
        paragraph_converter.add_markdown(markdown_text=f"User: {msg}")

        new_element = document.createElement("div")
        new_element.innerHTML = paragraph_converter.get()

        self.chat_window.appendChild(new_element)


