#backend-api/services/pdf_parser.py
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file_path: str) -> str:
    """
    Extract text content from a PDF file using PyMuPDF.
    """
    text = ""
    with fitz.open(pdf_file_path) as doc:
        for page in doc:
            text += page.get_text("text")
    return text.strip()
