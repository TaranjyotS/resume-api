from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.document_parser import extract_text

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/extract-text")
async def extract_document_text(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = extract_text(file.filename or "uploaded", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not read document: {exc}") from exc
    if not text:
        raise HTTPException(status_code=422, detail="No readable text found in the uploaded document.")
    return {"filename": file.filename, "characters": len(text), "text": text}
