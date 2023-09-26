class Tool:
    def __init__(self):
        self.name = None
        self.is_enabled = None

    def handle_call(self, args_dict) -> None:
        pass

    def get_json_doc(self) -> dict:
        pass

