import openai
import os
import configparser

from src.l2_lotus_core.m1_models.model_definitions import OpenAI_ModelTypes


# ---------------------------------------------------------

def setup():
    while True:
        try:
            set_api_key()
            print(f'[Debug]: API key is set')
            break
        except:
            pass

CONFIG_SECTION = 'API'
API_KEY_FIELD = 'openai_key'

def set_api_key() -> None:
    home = os.path.expanduser("~")
    config_path = os.path.join(home, 'm1_settings.ini')
    config = configparser.ConfigParser()

    try:
        config.read(config_path)
        key = config.get(CONFIG_SECTION, API_KEY_FIELD)
        test_api_key(key)
        print(f'[Debug]: Valid API key obtained from m1_settings file located at {config_path}')

    except Exception as err:
        print(f'[Debug]: Failed to retrieve valid API key from m1_settings file: {err}')
        key = input('[Debug]: Enter API key manually:\n')
        test_api_key(key)
        save_key_to_file(config,config_path,key)


def test_api_key(key : str) -> None:
    try:
        openai.api_key = key
        args_dict = {
            'model': OpenAI_ModelTypes.gpt_35_4k,
            'messages': [{'role' : 'user', 'content' : 'This is a test'}],
            'max_tokens' : 5
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