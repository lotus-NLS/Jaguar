import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import customtkinter as ctk

from s1_conversation.Conversation import ConversationParticipant,ConversationEntry,Channel,Dialogue_Roles
from s3_equipped_agent.BasicAgent import BasicAgent

# ---------------------------------------------------------


class GUI_User(ConversationParticipant):

    def __init__(self):
        super().__init__(Dialogue_Roles.user)
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

    def _reaction_protocol(self, dialogue_line : ConversationEntry):
        role = dialogue_line.get_role()
        msg = dialogue_line.get_content()
        self.display_message(f'{role}: {msg}\n')

    def display_message(self, message):
        self.message_area.configure(state='normal')
        self.message_area.insert(tk.END, message)
        self.message_area.configure(state='disabled')


if __name__ == "__main__":

    the_conversation = Channel()
    the_user = GUI_User()
    the_bot = BasicAgent()

    for participant in [the_user, the_bot]:
        the_conversation.add_participant(participant)

    the_user.window.mainloop()


