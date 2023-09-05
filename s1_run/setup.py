import openai
import os
import configparser
from s3_agent.Agent import Models
from s4_conversation.s0_ConversationParticipant import ConversationEntry,DialogueRole

def setup():
    while True:
        try:
            set_api_key()
        except:
            pass

CONFIG_SECTION = 'API'
API_KEY_FIELD = 'openai_key'

def set_api_key() -> None:
    home = os.path.expanduser("~")
    config_path = os.path.join(home, 'settings.ini')
    config = configparser.ConfigParser()

    try:
        config.read(config_path)
        key = config.get(CONFIG_SECTION, API_KEY_FIELD)
        test_api_key(key)
        save_key_to_file(config, config_path, key)

    except Exception as err:
        print(f'[Debug]: Failed to retrieve valid API key from settings file: {err}')
        key = input('[Debug]: Enter API key manually:\n')
        test_api_key(key)
        save_key_to_file(config,config_path,key)


def test_api_key(key : str) -> None:
    try:
        openai.api_key = key
        args_dict = {
            'model': Models.gpt_40_8k,
            'messages': [ConversationEntry(role=DialogueRole.user(), msg='This is a test')],
        }
        openai.ChatCompletion.create(**args_dict)

    except Exception as err:
        print(f'[Debug]: Error after test run:\n{err}')
        raise ValueError('Invalid API key')


def save_key_to_file(config, config_path, key):
    if CONFIG_SECTION not in config.sections():
        config.add_section(CONFIG_SECTION)
    config.set(CONFIG_SECTION, API_KEY_FIELD, key)
    with open(config_path, 'w') as f:
        config.write(f)
    print(f'[Debug]: API key saved to {config_path}')