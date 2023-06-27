import dearpygui.dearpygui as dpg
import threading
import openai

openai.api_key = [Place the key here]  # Replace with your actual OpenAI key
# ----------------------------------------------------



import os

api_key = os.environ.get('openai_key')
if api_key is None:
    print("Key not found.")
else:
    print("Key:", api_key)


import os

# Get all environment variables
env_vars = os.environ

# Print all environment variables
for var, value in env_vars.items():
    print(f"{var}={value}")


# ----------------------------------------------------
class ChatApplication:

    def __init__(self,init_msg):
        dpg.create_context()
        dpg.create_viewport(title="Chat with GPT-3.5", width=600, height=300)
        self.window_id = dpg.add_window(label="Chat Window")
        self.conversation = [{"role": "system", "content": f"{init_msg}"}]
        self.message_area = dpg.add_text("", parent=self.window_id)
        self.input_area = dpg.add_input_text(parent=self.window_id, on_enter=True, callback=self.send_message)
        dpg.add_button(parent=self.window_id, label="Send", callback=self.send_message)

    def send_message(self, sender, data):
        message = dpg.get_value(self.input_area)
        if message:
            self.conversation.append({"role": "user", "content": message})
            self.display_message(f'You: {message}\n')
            dpg.set_value(self.input_area, "")

            threading.Thread(target=self.get_response).start()

    def get_response(self):
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.conversation)
            chatbot_message = response['choices'][0]['message']['content'].strip()
            self.display_message(f'GPT-3.5: {chatbot_message}\n')
            self.conversation.append({"role": "assistant", "content": chatbot_message})
        except Exception as e:
            self.display_message(f'Error: Unable to get response from GPT-3.5. {str(e)}\n')

    def display_message(self, message):
        dpg.set_value(self.message_area, dpg.get_value(self.message_area) + message)


# Open a file
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
