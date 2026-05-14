# AI Resume Intelligence

A full-stack, Ollama-first AI resume intelligence platform for tailoring resumes to job descriptions, generating ATS-friendly packages, and tracking job applications.

The project is designed as a portfolio-grade Python/full-stack system: FastAPI backend, React frontend, local LLM support through Ollama, extensible cloud model providers, document parsing, scoring logic, tests, Docker, Postman, and Jenkins CI/CD.

## Core Features

- Candidate login/register UI and auth API
- Candidate resume workspace
- Job description workspace
- PDF, DOCX, and TXT upload for resumes and job descriptions
- Text extraction from uploaded documents
- ATS keyword score for uploaded resume
- Projected ATS score for tailored resume
- Tailored ATS-friendly resume draft
- Personalized cover letter
- Recruiter email
- LinkedIn message under 300 characters
- Interview questions and preparation links based on the role
- Application tracker/logs tab for positions the candidate applied to
- Ollama as the default local AI provider
- Provider abstraction for future OpenAI, Claude, Gemini, AWS Bedrock, and Azure OpenAI support
- Backend tests, scoring tests, parser tests, and API-flow tests
- Postman collection
- Jenkins pipeline
- Docker Compose structure

## Architecture

```text
frontend/ React + Vite UI
    ↓
backend/ FastAPI API layer
    ├── auth routes
    ├── candidate/job routes
    ├── document extraction routes
    ├── AI tailoring routes
    ├── application tracking routes
    └── analytics routes
    ↓
AI provider layer
    ├── OllamaProvider       default local/private provider
    ├── CloudProviderStub    placeholder for OpenAI/Claude/Gemini/etc.
    ↓
Storage
    ├── SQLite locally
    ├── PostgreSQL for production
    └── S3 for uploaded documents in production
```

## Recommended Local Setup

### 1. Start Ollama

Ollama may already run in the background on Windows. Check first:

```bash
ollama list
```

Pull the models:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

If Ollama is not running:

```bash
ollama serve
```

If you see `bind: Only one usage of each socket address...`, Ollama is already running.

### 2. Start Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Git Bash/Linux/macOS
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Optional now: backend auto-creates backend/.env and JWT_SECRET if missing
# cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/docs
```

### Automatic JWT Secret Handling

For local development, the backend now automatically creates `backend/.env` if it is missing. It also replaces placeholder values such as:

```env
JWT_SECRET=auto-generate-for-local-dev
JWT_SECRET=replace-this-with-a-long-random-secret
JWT_SECRET=change-me-in-production
```

with a strong random JWT secret and persists it in `backend/.env`. Existing real secrets are never overwritten.

For production, inject `JWT_SECRET` through your deployment platform, Docker/Kubernetes secrets, AWS Secrets Manager, Vault, Vercel/Render/AWS environment variables, etc.

### 3. Start Frontend

Use Node `20.19+` or `22.12+`.

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

If you open the app from another device using a LAN URL such as `http://192.168.1.x:5173`, the backend CORS config now supports it.

## How to Use the App

1. Open the frontend.
2. Go to **Login / Register** and create a demo account.
3. Go to **Workspace**.
4. Upload a PDF/DOCX/TXT resume or paste resume text.
5. Upload a PDF/DOCX/TXT job description or paste the JD.
6. Click **Analyze + Tailor**. The app creates the candidate/job records internally and generates the tailored package.
7. For registered candidates, an application log is automatically created. Guest mode does not save logs.
8. Review:
   - uploaded resume ATS score
   - tailored resume ATS score
   - ATS-friendly resume
   - cover letter
   - recruiter email
   - LinkedIn message
   - interview questions
   - useful interview preparation links
9. Go to **Application Logs** to view or edit the automatically created log, including the full tailored package summary.

## API Examples

Create candidate:

```bash
curl -X POST http://localhost:8000/api/v1/candidates \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Demo Candidate","target_role":"Python Developer","location":"Canada","resume_text":"Python FastAPI AWS Docker SQL","skills":"Python, FastAPI"}'
```

Create job:

```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"company":"DemoCo","title":"Backend Developer","description":"Python FastAPI AWS SQL Docker APIs"}'
```

Extract document text:

```bash
curl -X POST http://localhost:8000/api/v1/documents/extract-text \
  -F "file=@resume.pdf"
```

Generate tailored package:

```bash
curl -X POST http://localhost:8000/api/v1/ai/tailor \
  -H "Content-Type: application/json" \
  -d '{"candidate_id":1,"job_id":1,"provider":"ollama","model":"llama3.1:8b"}'
```

## Postman

Import:

```text
postman/Resume-AI-Platform.postman_collection.json
```

Set `baseUrl` to:

```text
http://localhost:8000
```

## Tests and Quality Checks

```bash
cd backend
pytest --cov=app --cov-report=term-missing
ruff check app tests
bandit -r app -ll
```

Current test areas:

- health endpoint
- candidate creation
- job creation
- application logs
- text document extraction
- ATS scoring
- projected scoring

## Jenkins Pipeline

The Jenkinsfile is located at:

```text
infra/jenkins/Jenkinsfile
```

Pipeline stages:

1. Backend install
2. Backend lint using Ruff
3. Security scan using Bandit
4. Pytest with coverage
5. Frontend install/build

Basic Jenkins setup:

1. Create a new Jenkins Pipeline job.
2. Point it to your GitHub repository.
3. Set the script path to:

```text
infra/jenkins/Jenkinsfile
```

4. Add tools on Jenkins agent:
   - Python 3.11+
   - Node 20.19+ or 22.12+
   - npm
5. Run the pipeline.

For production, add stages for Docker image build, Docker image scan, push to registry, and deployment to EC2/ECS.

## CI/CD Behavior

The Jenkinsfile is included, but Jenkins will **not** run automatically just because the code is pushed to GitHub unless Jenkins is connected to the repository. To make it automatic, configure one of these:

1. GitHub webhook pointing to your Jenkins server.
2. Jenkins GitHub Branch Source plugin with webhook or periodic scan.
3. A Jenkins Multi-branch Pipeline job connected to your GitHub repository.

Once configured, every push or pull request can trigger the pipeline. Without that setup, you can still run the pipeline manually from Jenkins.

## Docker

```bash
docker compose up --build
```

For local LLM calls, keep Ollama running on the host machine. The backend uses `OLLAMA_BASE_URL=http://localhost:11434` when running directly. For Docker networking, update the env value depending on your OS if the container cannot reach the host.
