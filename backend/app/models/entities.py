from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, index=True, default="candidate")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    preferred_provider: Mapped[str] = mapped_column(String(50), default="ollama")
    preferred_model: Mapped[str] = mapped_column(String(100), default="llama3.1:8b")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class Candidate(Base):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), default=1)
    full_name: Mapped[str] = mapped_column(String(255))
    target_role: Mapped[str] = mapped_column(String(255), default="Target Role")
    location: Mapped[str] = mapped_column(String(255), default="")
    resume_text: Mapped[str] = mapped_column(Text)
    skills: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    user = relationship("User")

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), default=1)
    company: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    seniority: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    user = relationship("User")

class GenerationResult(Base):
    __tablename__ = "generation_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id"))
    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    ats_score: Mapped[float] = mapped_column(Float, default=0)
    improved_ats_score: Mapped[float] = mapped_column(Float, default=0)
    output_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class ApplicationLog(Base):
    __tablename__ = "application_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    job_id: Mapped[int | None] = mapped_column(ForeignKey("job_descriptions.id"), nullable=True)
    result_id: Mapped[int | None] = mapped_column(ForeignKey("generation_results.id"), nullable=True)
    company: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(String(255), default="")
    portal_url: Mapped[str] = mapped_column(String(1000), default="")
    status: Mapped[str] = mapped_column(String(100), default="draft")
    summary: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    candidate = relationship("Candidate")
    job = relationship("JobDescription")
    result = relationship("GenerationResult")
