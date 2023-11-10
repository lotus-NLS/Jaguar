from browser import window

# ----------------------------------------------


# converter = new showdown.Converter(),
# text      = '# hello, markdown!',
# html      = converter.makeHtml(text);

def convert_markdown_to_html(markdown_text):
    converter = window.showdown.Converter.new()

    print(converter)
    html = converter.makeHtml(markdown_text)
    return html