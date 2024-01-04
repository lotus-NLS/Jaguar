from pypdf import PdfReader

def get_txt_file_content(location : str) -> str:
    with open(location, 'r') as file:
        file_content = file.read()
    return file_content


def get_pdf_file_content(location : str) -> str:
    pdf_file = open(location, 'rb')
    pdf_reader = PdfReader(pdf_file)

    pdf_content = ''
    for page in pdf_reader.pages:
        pdf_content += page.extract_text()

    # Close the PDF file
    pdf_file.close()

    return pdf_content