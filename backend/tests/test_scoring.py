from app.services.scoring import keyword_score, final_ats_score, section_score, projected_improved_score

def test_keyword_score_matches_terms():
    score, missing = keyword_score("Python FastAPI AWS", "Python FastAPI AWS Docker Kubernetes")
    assert score > 0
    assert "docker" in missing or "kubernetes" in missing

def test_section_score_detects_resume_sections():
    resume = "Skills: Python\nExperience: Backend Developer\nEducation: MSc\nProjects: API"
    assert section_score(resume) == 100

def test_final_score_range():
    assert 0 <= final_ats_score(70, "Skills Experience Education") <= 100

def test_projected_improved_score_is_capped():
    assert projected_improved_score(97, 20) <= 98
