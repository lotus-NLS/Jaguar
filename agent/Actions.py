from openai.openai_object import OpenAIObject
from typing import Union

class Action:
    def __init__(self, openAI_response : dict):
        self._response : dict = openAI_response

        try:
            self._best_response : dict = openAI_response['choices'][0]['message']
        except:
            print('[Debug]: Failed to retrieve response from OpenAI')
            self._best_response  : dict = {}

    # To my knowledge 'content' is always a key in the dict but not always filled with text
    def get_text_content(self) -> Union[str,None]:
        content = self._best_response['content'] if 'content' in self._best_response else None
        return content if isinstance(content,str) else None


    def get_function_call(self) -> Union[dict,None]:
        funct_call = self._best_response['function_call'] if 'function_call' in self._best_response else None
        return funct_call if isinstance(funct_call,dict) else None

