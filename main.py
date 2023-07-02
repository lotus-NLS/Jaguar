import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import customtkinter as ctk
import threading
import openai
import os

api_key = os.environ.get('openai_key')
if api_key is None:
    print("Key not found. Aborting program ...")
    exit(1)

openai.api_key = api_key


class ChatApplication:

    def __init__(self, init_msg):
        self.width = 600
        self.height = 600

        self.window = tk.Tk()
        self.window.title("Chat with GPT-3.5")
        self.window.geometry(f'{self.width}x{self.height}')
        self.window.configure(bg='#D3D3D3')

        self.conversation = [{"role": "system", "content": f"{init_msg}"}]
        self.font = ctk.CTkFont(family='Helvetica', size=18)

        self.message_area = ScrolledText(self.window, bg='white', fg='black', font=self.font)
        self.message_area.pack(fill='both', expand=True)

        self.input_area = ctk.CTkEntry(self.window, fg_color=('black', 'black'), bg_color=('white', 'white'), font=self.font)
        self.input_area.pack(fill='x')

        send_button = ctk.CTkButton(self.window, text="Send", command=self.send_message,
                                    fg_color=('#FFFFFF', '#FFFFFF'), bg_color=('#0000FF', '#0000FF'), font=self.font)
        send_button.pack(fill='x')

        self.input_area.bind("<Return>", self.send_message)


    def send_message(self, event=None):
        message = self.input_area.get()
        if message:
            self.conversation.append({"role": "user", "content": message})
            self.display_message(f'You: {message}\n')
            self.input_area.delete(0, 'end')

            threading.Thread(target=self.get_response).start()

    def get_response(self):
        try:
            # start_time = time.time()
            chatbot_message = ""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.conversation,
                stream=True
            )

            self.display_message(f'GPT-3.5: ')  # Display assistant's name once before the message starts

            for chunk in response:
                # chunk_time = time.time() - start_time  # calculate the time delay of the chunk
                if chunk['choices'][0]['delta']:
                    to_append = chunk['choices'][0]['delta']['content']  # extract the message
                else:
                    to_append = '\n'

                chatbot_message += to_append  # append the chunk to the message
                self.display_message(f'{to_append}')  # Display each chunk as it arrives
                self.conversation.append({"role": "assistant", "content": chatbot_message})

        except Exception as e:
            self.display_message(f'Error: Unable to get response from GPT-3.5. {str(e)}\n')

    def display_message(self, message):
        self.message_area.configure(state='normal')
        self.message_area.insert(tk.END, message)
        self.message_area.configure(state='disabled')


def read_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data


if __name__ == "__main__":
    file_path = 'prompt'
    prompt_str = read_file(file_path)
    app = ChatApplication(prompt_str)
    app.window.mainloop()
