from src.l5_conversation.l0_conversation_participant import ConversationParticipant,DialogueRole
from src.l3_agent.agent import Agent
from src.l2_toolbox.file_io import READ, WRITE
from src.l2_toolbox.run import RUN

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import customtkinter as ctk

# ---------------------------------------------------------

class DefaultAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_tools(tool_types=[READ, WRITE, RUN])


class User(ConversationParticipant):
    def __init__(self):
        super(User, self).__init__(role=DialogueRole.user())


# TODO: This must be separated into two classes. The user must be separated from the GUI
class GUI_User(ConversationParticipant):
    def __init__(self):
        super().__init__(DialogueRole.user())
        self.width = 600
        self.height = 600

        self.window = tk.Tk()
        self.window.title("Chat with GPT-4")
        self.window.geometry(f'{self.width}x{self.height}')
        self.window.configure(bg='#D3D3D3')

        self.font = ctk.CTkFont(family='Helvetica', size=18)

        self.message_area = ScrolledText(self.window, bg='white', fg='black', font=self.font)
        self.message_area.pack(fill='both', expand=True)

        self.input_area = tk.Entry(self.window, fg='black', bg='white', font=self.font)
        self.input_area.pack(fill='x')
        self.input_area.bind("<Return>", self.send_message)

        send_button = tk.Button(self.window, text="Send", command=self.send_message, fg='white', bg='#87CEFA',
                                font=self.font)

        send_button.pack(fill='x')

    def send_message(self, event=None):
        _ = event
        self.speak(self.input_area.get())
        self.input_area.delete(0, 'end')

    def _reaction_protocol(self, conversation_entry):
        role = conversation_entry.get_role()
        msg = conversation_entry.get_content()
        self.display_message(f'{role}: {msg}\n')

    def display_message(self, message):
        self.message_area.configure(state='normal')
        self.message_area.insert(tk.END, message)
        self.message_area.configure(state='disabled')