class Models:
    # The 0613 models (06.13.23, the date of the API updates (https://openai.com/blog/function-calling-and-other-api-updates)
    # support function calling
    # But gpt-4 or gpt-3.5-turbo will always point to the newest version anyway

    gpt_35_4k = 'gpt-3.5-turbo-0613'
    gpt_35_16k = 'gpt-3.5-turbo-16k-0613'
    gpt_40_8k = 'gpt-4-0613'
    gpt_40_32k = 'gpt-4-32k-0613'

    @staticmethod
    def get_test_model():
        return Models.gpt_35_4k