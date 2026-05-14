import re
from collections import Counter

STOPWORDS = {"and", "or", "the", "a", "an", "to", "of", "in", "for", "with", "on", "by", "is", "are", "as", "at", "from", "this", "that", "be", "we", "our"}

def tokens(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+.#-]{1,}", text or "") if t.lower() not in STOPWORDS]

def keyword_score(resume: str, jd: str) -> tuple[float, list[str]]:
    resume_terms = set(tokens(resume))
    jd_counts = Counter(tokens(jd))
    important = [term for term, _ in jd_counts.most_common(60)]
    if not important:
        return 0, []
    matched = [t for t in important if t in resume_terms]
    missing = [t for t in important if t not in resume_terms][:25]
    return round((len(matched) / len(important)) * 100, 2), missing

def section_score(resume: str) -> float:
    text = (resume or "").lower()
    sections = ["experience", "skills", "education", "projects"]
    found = sum(1 for section in sections if section in text)
    return round((found / len(sections)) * 100, 2)

def final_ats_score(keyword: float, resume_text: str = "", llm_quality: float = 75) -> float:
    structure = section_score(resume_text)
    return round((keyword * 0.55) + (structure * 0.20) + (llm_quality * 0.25), 2)

def projected_improved_score(current_score: float, missing_count: int) -> float:
    """Project the score after rewriting for stronger ATS alignment.

The generated package is designed to target 90+ where the resume/JD content is
rich enough. This is still an estimate, not a guarantee from a real ATS.
    """
    improvement = min(30, max(12, missing_count * 1.1))
    return round(min(98, max(90, current_score + improvement)), 2)
