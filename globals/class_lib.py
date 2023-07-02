class Tools:

    @staticmethod
    def read_file(filename):
        with open(filename, 'r') as file:
            return file.read()

    @staticmethod
    def write_file(filename, content):
        with open(filename, 'w') as file:
            file.write(content)
        return True

    @staticmethod
    def protocol_read_write_file(message):
        return message.split(": ")[1].split(", ")


class Models:
    gpt_35_16k = 'gpt-3.5-turbo-16k'
    gpt_35_4k = 'gpt-3.5-turbo'
    gpt_40_32k = 'gpt-4-32k-0613'
    gpt_40_8k = 'gpt-4-0613'


class Roles:
    user = 'user'
    agent = 'assistant'
    system = 'system'