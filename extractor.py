import io
from typing import Optional

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file bytes using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        extracted_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text.append(text.strip())
        return "\n\n".join(extracted_text)
    except ImportError:
        raise RuntimeError("pypdf is not installed. Please install it with 'pip install pypdf'.")
    except Exception as e:
        raise ValueError(f"Failed to parse PDF document: {str(e)}")

def extract_text_from_upload(uploaded_file) -> str:
    """Extract text from an uploaded Streamlit file (PDF or TXT)."""
    if uploaded_file is None:
        return ""
    
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    
    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif file_name.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="ignore")
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or TXT file.")

