# Architecture

The platform is an Ollama-first full-stack AI SaaS-style project.

## Flow

Frontend → FastAPI API Gateway → Domain routers/services → AI Provider Router → Ollama or cloud provider → PostgreSQL/SQLite + Redis + analytics.

## Core Services

- Auth service: user registration, login, JWT/API-key-ready design.
- Candidate service: candidate profile, resume text, skills, target role.
- Job service: job descriptions and seniority metadata.
- AI service: ATS score, missing keywords, tailored resume, cover letter, recruiter email, LinkedIn message.
- Analytics service: candidate/job/run counts and average ATS score.

## AI Provider Strategy

Ollama is primary for privacy and zero API cost. Cloud providers can be added behind the same `BaseLLMProvider` interface.

## Why this architecture

It separates UI, API, data, AI orchestration, and analytics. This makes the project easier to test, deploy, scale, and explain in interviews.
