from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import Candidate, JobDescription
from app.schemas.dto import CandidateCreate, JobCreate

router = APIRouter(tags=["candidates-jobs"])

@router.post("/candidates")
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    candidate = Candidate(user_id=1, **payload.model_dump())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return {"id": candidate.id, "full_name": candidate.full_name}

@router.post("/jobs")
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = JobDescription(user_id=1, **payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "title": job.title, "company": job.company}

@router.get("/candidates")
def list_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).order_by(Candidate.id.desc()).all()

@router.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    return db.query(JobDescription).order_by(JobDescription.id.desc()).all()
