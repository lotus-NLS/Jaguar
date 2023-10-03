import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import Callable, Optional

import customtkinter as ctk

from src.l3_lotus_core.m0_conversation.channel import Channel
from src.l3_lotus_core.m0_conversation import Entry

# ---------------------------------------------------------


class GUI_Element:
    def __init__(self,*args,**kwargs):
        self.sub_elements = None

    def run(self):
        pass


class ChatGUI(GUI_Element):
    def __init__(self, send_callback : Callable[[str],None], channel : Channel):
        super(ChatGUI, self).__init__()
        self.channel : Optional[Channel] = channel
        self.join_channel(channel)

        self.window = tk.Tk()
        self.font = ctk.CTkFont(family='Helvetica', size=18)
        self.msg_area = ScrolledText(self.window, bg='white', fg='black', font=self.font)
        self.send_callback = send_callback
        self.input_area = tk.Entry(self.window, fg='black', bg='white', font=self.font)


        window = self.window
        msg_area = self.msg_area
        font = self.font
        input_area = self.input_area

        window.title("Chat with GPT-4")
        window.geometry('600x600')
        window.configure(bg='#D3D3D3')
        msg_area.pack(fill='both', expand=True)

        input_area.pack(fill='x')
        input_area.bind("<Return>", lambda event: self.send_msg(input_area.get()))

        send_button = tk.Button(self.window, text="Send", command=lambda: send_callback(input_area.get()),
                                fg='white', bg='#87CEFA', font=font)
        send_button.pack(fill='x')

    def leave_channel(self):
        if not self.channel is None:
            self.channel.listener_loggers.remove(self.display_conversation_entry)
            self.channel = None

    def join_channel(self, channel : Channel):
        channel.listener_loggers.append(self.display_conversation_entry)
        self.channel = channel

    def run(self):
        self.window.mainloop()

    def send_msg(self, msg : str):
        self.send_callback(msg)
        self.input_area.delete(0, 'end')

    def display_conversation_entry(self, entry : Entry):
        role = entry.get_role()
        msg = entry.get_content()
        self.msg_area.configure(state='normal')
        self.msg_area.insert(tk.END, chars=f'{role}: {msg}\n')
        self.msg_area.configure(state='disabled')
