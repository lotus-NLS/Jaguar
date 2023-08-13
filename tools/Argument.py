class Arg:
    def __init__(self, name: str, dtype : type, description: str, value = None):
        self.name = name
        self.dtype = dtype
        self.description = description
        self.val = value

    def generate_argument_doc(self):
        arg_doc = {
            self.name: {
                'type': f'{self.dtype}',
                'description': f'{self.description}'
            }
        }
        return arg_doc