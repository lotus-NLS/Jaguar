import dearpygui.dearpygui as dpg
import threading
import openai
import os

api_key = os.environ.get('openai_key')
if api_key is None:
    print("Key not found. Aborting program ...")
    exit(1)

openai.api_key = api_key

class ChatApplication:

    def __init__(self,init_msg):
        self.width = 600
        self.height = 600

        dpg.create_context()
        self.window_id = dpg.add_window(label="Chat Window", no_title_bar=True, no_move=True, no_resize=True,
                                        no_collapse=True, horizontal_scrollbar=True, width=self.width,
                                        height=self.height, menubar=False)

        self.conversation = [{"role": "system", "content": f"{init_msg}"}]
        self.child_window = dpg.add_child(parent=self.window_id, horizontal_scrollbar=False)  # Add this line
        self.message_area = dpg.add_text("", parent=self.child_window,wrap=self.get_text_length())  # Modify this line
        self.input_area = dpg.add_input_text(parent=self.window_id, width=self.width, on_enter=True,
                                             callback=self.send_message)

        dpg.create_viewport(title="Chat with GPT-3.5", width=self.width, height=self.height)
        dpg.add_button(parent=self.window_id, label="Send", callback=self.send_message)
        dpg.set_viewport_resize_callback(self.on_resize)

    def get_text_length(self):
        return int(0.9*self.width)

    def send_message(self, sender, data):
        message = dpg.get_value(self.input_area)
        if message:
            self.conversation.append({"role": "user", "content": message})
            self.display_message(f'You: {message}\n')
            dpg.set_value(self.input_area, "")

            threading.Thread(target=self.get_response).start()
        dpg.focus_item(self.input_area)


    def get_response(self):
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=self.conversation)
            chatbot_message = response['choices'][0]['message']['content'].strip()
            self.display_message(f'GPT-3.5: {chatbot_message}\n')
            self.conversation.append({"role": "assistant", "content": chatbot_message})
        except Exception as e:
            self.display_message(f'Error: Unable to get response from GPT-3.5. {str(e)}\n')

    def display_message(self, message):
        dpg.set_value(self.message_area, dpg.get_value(self.message_area) + message)
        dpg.configure_item(self.child_window, width=self.width)  # Add this line


    def on_resize(self, sender, data):
        print('Triggered callback!')
        self.height = dpg.get_viewport_height()
        self.width = dpg.get_viewport_width()
        dpg.configure_item(self.window_id, width=self.width, height=self.height)
        dpg.configure_item(self.message_area, wrap=self.get_text_length())  # Update the wrap attribute here


def read_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data


if __name__ == "__main__":
    file_path = 'prompt'
    prompt_str = read_file(file_path)

    app = ChatApplication(prompt_str)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
