from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import Candidate, JobDescription, GenerationResult

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return {
        "candidates": db.query(Candidate).count(),
        "jobs": db.query(JobDescription).count(),
        "tailoring_runs": db.query(GenerationResult).count(),
        "average_ats_score": round(sum(r.ats_score for r in db.query(GenerationResult).all()) / max(db.query(GenerationResult).count(), 1), 2),
    }
