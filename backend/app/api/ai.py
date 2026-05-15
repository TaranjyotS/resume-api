import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import Candidate, JobDescription, GenerationResult, ApplicationLog
from app.schemas.dto import TailorRequest
from app.services.ai_router import ai_router
from app.services.scoring import keyword_score, final_ats_score, projected_improved_score
from app.services.prompts import tailoring_prompt, interview_resource_links, infer_company, infer_job_title

router = APIRouter(prefix="/ai", tags=["ai"])

def _safe_json(raw: str) -> dict:
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {"raw_generation": raw}
    except Exception:
        return {"raw_generation": raw}

def _bullets_from_resume(resume: str) -> str:
    lines = [line.strip() for line in resume.splitlines() if len(line.strip()) > 20]
    bullets = lines[:8] or ["Built scalable software systems and delivered measurable engineering outcomes."]
    return "\n".join(f"• {b}" for b in bullets)

def _extract_name(resume: str, fallback: str) -> str:
    for line in resume.splitlines():
        clean = line.strip()
        if 2 < len(clean) < 80 and not any(x in clean.lower() for x in ['@', 'http', 'linkedin', 'github', 'professional summary', 'skills']):
            return clean.title()
    return fallback or 'Candidate'

def _tailored_resume_preserving_format(candidate: Candidate, job: JobDescription, missing: list[str]) -> str:
    """Create a practical fallback resume that preserves the user's plain-text layout.

    This is used when the LLM is unavailable or returns invalid JSON. It keeps
    recognizable sections and contact/context from the original resume instead
    of producing a totally different template.
    """
    role = infer_job_title(job.description)
    keywords = ', '.join(missing[:16]) if missing else 'backend systems, APIs, cloud infrastructure, distributed systems, testing, automation'
    original_lines = [line.rstrip() for line in candidate.resume_text.splitlines()]
    name = _extract_name(candidate.resume_text, candidate.full_name)
    contact = []
    for line in original_lines[:12]:
        if line.strip() and (('@' in line) or ('linkedin' in line.lower()) or ('github' in line.lower()) or (',' in line and len(line) < 80) or line.strip().isupper()):
            contact.append(line.strip())
    contact = contact[:5] or [name]
    experience_bullets = _bullets_from_resume(candidate.resume_text)
    return (
        f"{name}\n"
        + "\n".join(dict.fromkeys(contact))
        + f"\n\nTARGET ROLE\n{role}\n\n"
        + "PROFESSIONAL SUMMARY\n"
        + f"Software Engineer with 5+ years of experience tailored for {role} roles, combining backend engineering, API design, cloud-native development, CI/CD automation, testing, and production support. Experienced in building reliable, scalable, and maintainable systems while translating business requirements into secure software solutions. This ATS-focused version preserves the candidate's original resume structure while strengthening alignment with job keywords such as {keywords}.\n\n"
        + "TECHNICAL SKILLS\n"
        + "Programming & Backend: Python, FastAPI, Flask, REST APIs, JavaScript/TypeScript, Node.js\n"
        + "Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, CI/CD, Git, observability, production support\n"
        + "Databases & Data: SQL, NoSQL, data pipelines, reporting, performance optimization\n"
        + f"Role Keywords: {keywords}\n\n"
        + "PROFESSIONAL EXPERIENCE\n"
        + experience_bullets
        + "\n• Designed, developed, and maintained backend services with clear API contracts, robust error handling, automated tests, and deployment-ready documentation.\n"
        + "• Improved maintainability and delivery quality through CI/CD workflows, code reviews, security checks, and production support practices.\n"
        + "• Collaborated with product, QA, data, and infrastructure teams to deliver scalable software aligned with business needs.\n\n"
        + "PROJECTS / SELECTED WORK\n"
        + "• Built and improved full-stack and backend systems involving APIs, cloud services, automation, analytics, and user-facing workflows.\n"
        + "• Applied AI/ML or automation workflows where relevant to improve productivity, quality, and decision support.\n\n"
        + "EDUCATION & CERTIFICATIONS\n"
        + "Preserve the user's original education and certification entries from the uploaded resume.\n\n"
        + "ORIGINAL RESUME CONTEXT PRESERVED FOR FINAL EDITING\n"
        + candidate.resume_text.strip()[:2500]
    )

def _local_fallback_package(candidate: Candidate, job: JobDescription, missing: list[str]) -> dict:
    keywords = ", ".join(missing[:18]) if missing else "the job's core technical keywords"
    role = infer_job_title(job.description)
    return {
        "ats_friendly_resume": _tailored_resume_preserving_format(candidate, job, missing),
        "cover_letter": (
            "Dear Hiring Team,\n\n"
            f"I am excited to apply for the {role} opportunity. The role appears to require someone who can contribute to reliable backend systems, API-driven product development, cloud infrastructure, automation, testing, and scalable engineering practices. My background aligns well with these needs through hands-on experience building backend and full-stack solutions, supporting production systems, and working with modern development workflows.\n\n"
            "Across my experience, I have worked with Python-based backend services, REST APIs, databases, CI/CD pipelines, cloud platforms, Docker/Kubernetes workflows, and automation-focused engineering. I have also contributed to systems where maintainability, reliability, performance, and clear documentation were important to successful delivery.\n\n"
            f"What interests me most about this opportunity is the chance to apply my technical background to the problems described in the job posting, particularly around {keywords}. I would bring a practical engineering mindset, strong ownership, and the ability to quickly understand existing systems while improving them incrementally.\n\n"
            "I would appreciate the opportunity to discuss how my experience can support your team's goals and contribute to high-quality software delivery. Thank you for your time and consideration.\n\n"
            "Sincerely,\nCandidate"
        ),
        "recruiter_email": (
            f"Subject: Application for {role} Opportunity\n\n"
            "Hi,\n\n"
            f"I hope you are doing well. I came across the {role} opportunity and wanted to reach out because the role appears closely aligned with my background in Python/backend engineering, API development, cloud-native systems, CI/CD automation, testing, and production-ready software delivery.\n\n"
            f"Based on the job description, the team is looking for experience around {keywords}. These areas connect strongly with my previous work building scalable backend systems, supporting data/application workflows, and delivering reliable software in collaborative engineering environments.\n\n"
            "I have attached my resume for your review and would appreciate the opportunity to connect if my profile looks aligned with the role.\n\n"
            "Best regards,\nCandidate"
        ),
        "linkedin_message": f"Hi, I came across your {role} opening. My background includes Python/backend engineering, APIs, cloud, CI/CD, and automation. I’d value the chance to connect and discuss how my experience aligns.",
        "interview_questions": [
            "Walk me through a backend system or API you designed end-to-end.",
            "How would you identify and reduce latency in a distributed service?",
            "How do you design database schemas for scale and maintainability?",
            "How do you test an API before production release?",
            "How would you secure sensitive user data in this system?",
            "Describe a time you improved reliability or reduced operational incidents.",
            "How do you approach CI/CD pipeline design?",
            "How would you containerize and deploy this application?",
            "How do you decide between synchronous and asynchronous processing?",
            "Which parts of your resume best match this job description and why?"
        ]
    }

@router.get("/health")
async def ai_health(provider: str = "ollama", model: str | None = None):
    selected = ai_router.get(provider)
    try:
        text = await selected.generate("Reply with only: ok", model)
        return {"status": "ok", "provider": provider, "model": model or "default", "sample": text[:80]}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"{provider} unavailable: {exc}") from exc

@router.post("/tailor")
async def tailor(payload: TailorRequest, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, payload.candidate_id)
    job = db.get(JobDescription, payload.job_id)
    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Candidate or job not found")

    if not job.title or job.title == "Target Role":
        job.title = infer_job_title(job.description)
    if not job.company:
        job.company = infer_company(job.description)

    key_score, missing = keyword_score(candidate.resume_text + " " + candidate.skills, job.description)
    current_score = final_ats_score(key_score, candidate.resume_text)
    improved_score = projected_improved_score(current_score, len(missing))
    prompt = tailoring_prompt(candidate.resume_text, job.description, missing, payload.tone)
    provider_name = payload.provider or "ollama"
    provider = ai_router.get(provider_name)
    provider_error = None

    try:
        generated = await provider.generate(prompt, payload.model)
        generated_json = _safe_json(generated)
        # If model returns raw prose instead of JSON, keep it but fill structured fields.
        if "raw_generation" in generated_json:
            generated_json = _local_fallback_package(candidate, job, missing) | {"model_raw_output": generated_json["raw_generation"]}
    except Exception as exc:
        provider_error = str(exc)
        generated_json = _local_fallback_package(candidate, job, missing)
        provider_name = "local-rule-fallback"

    resources = interview_resource_links(job.title, job.description)
    output = {
        "ats_score_uploaded_resume": current_score,
        "ats_score_tailored_resume": improved_score,
        "keyword_score": key_score,
        "missing_keywords": missing,
        "interview_preparation_links": resources,
        "package": generated_json,
        "provider_used": provider_name,
        "model_used": payload.model or "default",
        "provider_error": provider_error,
    }
    result = GenerationResult(candidate_id=candidate.id, job_id=job.id, provider=provider_name, model=payload.model or "default", ats_score=current_score, improved_ats_score=improved_score, output_json=json.dumps(output))
    db.add(result)
    db.commit()
    db.refresh(result)

    application_log_id = None
    if payload.create_application_log:
        summary = f"Full tailored package saved: resume, cover letter, recruiter email, LinkedIn message, interview questions, links. Uploaded ATS {current_score}; projected tailored ATS {improved_score}; keyword match {key_score}."
        log = ApplicationLog(candidate_id=candidate.id, job_id=job.id, result_id=result.id, company=job.company or "Company not specified", title=job.title or "Target Role", status="draft", summary=summary, notes="Generated tailored package")
        db.add(log)
        db.commit()
        db.refresh(log)
        application_log_id = log.id
    return {"result_id": result.id, "application_log_id": application_log_id, **output}
