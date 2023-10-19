# import openai
# import tiktoken
#
# from src.l3_lotus_core.m0_language.entry import Entry, DialogueRole
# from src.l2_lotus_agent.m2_action.action import Action
# from src.l2_lotus_agent.m2_action import ActionOptions, FunctCallOption
# from src.l2_lotus_agent.m1_models.llm import LLM
#
#

# class OpenAI_ModelTypes:
#     # The 0613 models support function calling. Earlier models do not.
#     # (06.13.23 is the date of the API updates https://openai.com/blog/function-calling-and-other-api-updates)
#     # 'gpt-4' or 'gpt-3.5-turbo' point to the newest version of either model available on the API
#
#     gpt_35_4k = 'gpt-3.5-turbo-0613'
#     gpt_35_16k = 'gpt-3.5-turbo-16k-0613'
#     gpt_40_8k = 'gpt-4-0613'
#     gpt_40_32k = 'gpt-4-32k-0613'
#
#     @staticmethod
#     def get_test_model():
#         return OpenAI_ModelTypes.gpt_35_4k
#
#
#
# # The cl100k_base encoder is the encoder used for 0314 and 0613 versions of 3.5 and 4
# # (https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
# class OpenAIModel(LLM):
#     def __init__(self, model_type : str):
#         super().__init__(model_type=model_type, encoding = tiktoken.get_encoding('cl100k_base'))
#
#
#
#     def get_action(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
#         file_path = "/home/daniel/openai_key.txt"
#         with open(file_path, "r") as file:
#             content = file.read()
#         openai.api_key = content
#
#         args_dict = {
#             'model': self._model_type,
#             'messages': entries,
#             'temperature': action_options.temperature
#         }
#
#         if action_options.get_funct_call_allowed():
#             args_dict['functions'] = tool_docs
#             args_dict['function_call'] = action_options.funct_call_options.get_openai_syntax()
#
#         if not action_options.max_tokens is None:
#             args_dict['max_tokens'] = action_options.max_tokens
#
#         self.log_request(entries=entries, tool_docs=tool_docs if action_options.get_funct_call_allowed() else None)
#         openai_response = openai.ChatCompletion.create(**args_dict)
#         self.log_response()
#
#         return Action(openai_response)
#
#
#     def log_request(self, entries : list[Entry], tool_docs : list[dict]):
#         # Alternatively exact tokens used up to and including response can be obtained via the response object
#         input_tokens_used = self.tokenizer.get_context_tokens(entries=entries, funct_docs=tool_docs)
#         print(f'[Debug]: Creating completion request; Currently at {input_tokens_used} input tokens used')
#         # print(f'[Debug]: Current conversation memory of {self._model_type}: [...] {str(entries)[-500:]}')
#
#
#     @staticmethod
#     def log_response():
#         # The Prompt tokens are the input_tokens that went into the request
#         # input_tokens_used = openai_response['usage']['prompt_tokens']
#         # print(f'Tokens in response: {input_tokens_used}')
#         print(f"[Debug]: Received response from the model.")
#
#
# # ----------------------------------------------------------------------------
#
# basic_entry = Entry(role=DialogueRole.system_role(),msg='Please greet our esteemed guests from Finland in both Finnish and in English')
# this_instance = OpenAIModel(model_type=OpenAI_ModelTypes.gpt_35_4k)
#
# action = this_instance.get_action(entries=[basic_entry],
#            tool_docs=[],
#            action_options=ActionOptions(funct_call_options=FunctCallOption.make_no_call_option())
#           )