from browser import window

class ParagraphConverter:
    def __init__(self):
        self.markdown_content = ""
        self.converter = window.showdown.Converter.new()

    def reset(self):
        self.markdown_content = ""

    def add_markdown(self, markdown_text):
        self.markdown_content += markdown_text + "\n"

    def get(self):
        return self.converter.makeHtml(self.markdown_content)