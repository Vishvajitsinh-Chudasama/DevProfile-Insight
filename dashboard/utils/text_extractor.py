import docx2txt
from PyPDF2 import PdfReader

def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        reader = PdfReader(file_path)
        return "\n".join([p.extract_text() or "" for p in reader.pages])
    elif file_path.lower().endswith(('.docx', '.doc')):
        return docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file type")
