from app.services.document_parser import extract_text

def test_extract_text_from_txt():
    assert extract_text("resume.txt", b"Python FastAPI AWS") == "Python FastAPI AWS"

def test_extract_text_rejects_unsupported_file():
    try:
        extract_text("resume.csv", b"a,b")
    except ValueError as exc:
        assert "Unsupported file type" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
