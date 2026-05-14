import re


def tailoring_prompt(resume_text: str, job_description: str, missing_keywords: list[str], tone: str) -> str:
    missing = ", ".join(missing_keywords[:20])
    return f"""
You are an expert ATS resume writer and career coach. Return ONLY valid JSON.

Create a complete tailored application package for this candidate and job.
The resume must be detailed, ATS-safe, and as close as possible to the uploaded/input resume format.
Preserve the candidate's original sections when possible: contact, summary, skills, experience, projects, education, and certifications.
Rewrite and expand bullets for relevance, measurable impact, and job-description alignment. Aim for a 90+ ATS-friendly package.
The cover letter must be 4-6 polished paragraphs and clearly reference the role requirements.
The recruiter email must include a subject and 2-4 concise but specific paragraphs.
The LinkedIn message must be under 300 characters but still personalized.
Provide exactly 10 interview questions tailored to the job.

Tone: {tone}
Missing keywords to include truthfully where possible: {missing}

JSON keys required:
{{
  "ats_friendly_resume": "complete tailored resume draft",
  "cover_letter": "complete cover letter",
  "recruiter_email": "subject plus full email",
  "linkedin_message": "short personalized LinkedIn message",
  "interview_questions": ["10 questions"]
}}

RESUME:
{resume_text[:7000]}

JOB DESCRIPTION:
{job_description[:6000]}
"""


def infer_job_title(description: str) -> str:
    """Infer a concise target role from a job description.

    Avoid returning full marketing/opening sentences such as
    "talented Backend Engineer to help design...". The function first
    checks explicit labels, then common role phrases, then keyword fallbacks.
    """
    text = re.sub(r"\s+", " ", description or "").strip()
    explicit = re.search(r"(?:job title|position|title|role)[:\-]\s*([^\n\|•]{3,90})", description or "", flags=re.I)
    if explicit:
        candidate = explicit.group(1).strip(" .:-")
        candidate = re.split(r"\s+(?:at|with|for|–|-)\s+", candidate, maxsplit=1, flags=re.I)[0]
        return candidate[:70].title()

    role_patterns = [
        r"\b(backend engineer)\b",
        r"\b(back[- ]end developer)\b",
        r"\b(python developer)\b",
        r"\b(python engineer)\b",
        r"\b(software engineer)\b",
        r"\b(full[- ]stack developer)\b",
        r"\b(full[- ]stack engineer)\b",
        r"\b(frontend engineer)\b",
        r"\b(front[- ]end developer)\b",
        r"\b(data engineer)\b",
        r"\b(machine learning engineer)\b",
        r"\b(devops engineer)\b",
        r"\b(cloud engineer)\b",
        r"\b(genai engineer)\b",
        r"\b(ai engineer)\b",
    ]
    for pattern in role_patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(1).replace("-", " ").title()

    looking = re.search(r"(?:looking for|hiring|seeking)\s+(?:a|an)?\s*([^\.]{3,120})", text, flags=re.I)
    if looking:
        phrase = looking.group(1)
        stop = re.split(r"\s+(?:to|who|with|for|that|to help)\s+", phrase, maxsplit=1, flags=re.I)[0]
        stop = re.sub(r"^(talented|experienced|senior|junior|intermediate|strong)\s+", "", stop, flags=re.I)
        if 3 <= len(stop) <= 70:
            return stop.strip(" .:-").title()

    lower = text.lower()
    if "backend" in lower or "back-end" in lower:
        return "Backend Engineer"
    if "python" in lower:
        return "Python Developer"
    if "data" in lower:
        return "Data Engineer"
    if "frontend" in lower or "front-end" in lower:
        return "Frontend Engineer"
    return "Target Role"


def infer_company(description: str) -> str:
    m = re.search(r"(?:company|about us|about the company)[:\-]\s*([^\n]{3,80})", description, flags=re.I)
    if m:
        return m.group(1).strip()[:80]
    return "Company not specified"


def interview_resource_links(title: str, description: str) -> list[dict]:
    text = f"{title} {description}".lower()
    links = [
        {"label": "STAR method behavioral interview prep", "url": "https://www.themuse.com/advice/star-interview-method"},
        {"label": "LeetCode interview practice", "url": "https://leetcode.com/problemset/"},
        {"label": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer"},
        {"label": "ByteByteGo system design", "url": "https://bytebytego.com/"},
    ]
    if "python" in text or "backend" in text:
        links += [
            {"label": "Real Python interview questions", "url": "https://realpython.com/python-interview-questions/"},
            {"label": "FastAPI official docs", "url": "https://fastapi.tiangolo.com/"},
        ]
    if "sql" in text or "database" in text:
        links.append({"label": "SQLBolt SQL practice", "url": "https://sqlbolt.com/"})
    if "aws" in text or "cloud" in text:
        links.append({"label": "AWS Skill Builder", "url": "https://skillbuilder.aws/"})
    if "kubernetes" in text or "docker" in text:
        links.append({"label": "Kubernetes official tutorials", "url": "https://kubernetes.io/docs/tutorials/"})
    return links[:10]
