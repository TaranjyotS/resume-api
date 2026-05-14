from io import BytesIO
import fitz  # PyMuPDF
from docx import Document

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def extract_text(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        with fitz.open(stream=content, filetype="pdf") as pdf:
            return "\n".join(page.get_text("text") for page in pdf).strip()
    if lower.endswith(".docx"):
        document = Document(BytesIO(content))
        return "\n".join(p.text for p in document.paragraphs if p.text.strip()).strip()
    if lower.endswith(".txt"):
        return content.decode("utf-8", errors="ignore").strip()
    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")
