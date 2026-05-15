import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import ApplicationLog, Candidate, JobDescription, GenerationResult
from app.schemas.dto import ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("")
def create_application(payload: dict, db: Session = Depends(get_db)):
    row = ApplicationLog(**payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("")
def list_applications(candidate_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(ApplicationLog).order_by(ApplicationLog.applied_at.desc())
    if candidate_id:
        query = query.filter(ApplicationLog.candidate_id == candidate_id)
    rows = query.all()
    return [{
        "id": r.id, "candidate_id": r.candidate_id, "job_id": r.job_id, "result_id": r.result_id,
        "company": r.company, "title": r.title, "status": r.status, "summary": getattr(r, "summary", ""), "notes": r.notes, "applied_at": r.applied_at.isoformat() if r.applied_at else None
    } for r in rows]

@router.get("/{application_id}")
def get_application(application_id: int, db: Session = Depends(get_db)):
    row = db.get(ApplicationLog, application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application log not found")
    candidate = db.get(Candidate, row.candidate_id)
    job = db.get(JobDescription, row.job_id) if row.job_id else None
    result = db.get(GenerationResult, row.result_id) if row.result_id else None
    return {
        "id": row.id, "company": row.company, "title": row.title, "status": row.status, "summary": getattr(row, "summary", ""), "notes": row.notes,
        "resume_text": candidate.resume_text if candidate else "",
        "job_description": job.description if job else "",
        "result": json.loads(result.output_json) if result else None,
    }

@router.patch("/{application_id}")
def update_application(application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)):
    row = db.get(ApplicationLog, application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application log not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row
