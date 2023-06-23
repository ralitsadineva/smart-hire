from pypdf import PdfReader

def read_pdf(file):
    reader = PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def page_count(file):
    reader = PdfReader(file)
    return len(reader.pages)