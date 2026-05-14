from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_candidate_and_job():
    candidate = client.post("/api/v1/candidates", json={
        "full_name": "Test Candidate",
        "target_role": "Python Developer",
        "location": "Canada",
        "resume_text": "Python FastAPI AWS Docker SQL",
        "skills": "Python, FastAPI"
    })
    assert candidate.status_code == 200, candidate.text
    assert candidate.json()["id"]

    job = client.post("/api/v1/jobs", json={
        "company": "TestCo",
        "title": "Backend Developer",
        "description": "Python FastAPI AWS SQL Docker backend APIs",
        "seniority": "mid"
    })
    assert job.status_code == 200, job.text
    assert job.json()["id"]

def test_application_log_create_and_list():
    candidate = client.post("/api/v1/candidates", json={
        "full_name": "Logger",
        "target_role": "Python Developer",
        "resume_text": "Python FastAPI testing"
    }).json()
    payload = {"candidate_id": candidate["id"], "company": "Demo", "title": "Python Dev", "status": "applied", "notes": "Submitted"}
    created = client.post("/api/v1/applications", json=payload)
    assert created.status_code == 200, created.text
    logs = client.get(f"/api/v1/applications?candidate_id={candidate['id']}")
    assert logs.status_code == 200
    assert len(logs.json()) >= 1
