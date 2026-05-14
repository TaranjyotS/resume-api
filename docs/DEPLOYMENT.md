# Deployment Guide

## Local mobile access

Run the backend and frontend on your laptop:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open the frontend from another device on the same Wi-Fi using your laptop IP:

```text
http://YOUR_LAPTOP_IP:5173
```

For example:

```text
http://192.168.1.74:5173
```

The backend CORS regex allows common LAN addresses.

## Frontend on Vercel

1. Push the repository to GitHub.
2. Import the `frontend` folder as the Vercel project root.
3. Set Node.js to `20.x` or `22.x`.
4. Add this environment variable:

```env
VITE_API_URL=https://YOUR_BACKEND_DOMAIN/api/v1
```

5. Deploy.

## Backend options

### Option A: Render/Railway/Fly.io

Deploy `backend` as a Python web service:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set production env vars:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB
JWT_SECRET=<secret-from-platform>
OLLAMA_BASE_URL=<your hosted Ollama endpoint or cloud provider service>
DEFAULT_GENERATION_MODEL=llama3.1:8b
DEFAULT_EMBEDDING_MODEL=nomic-embed-text
```

SQLite is fine locally, but use PostgreSQL for deployed multi-user usage.

### Option B: AWS EC2

1. Launch an EC2 instance.
2. Install Docker and Docker Compose.
3. Clone the repository.
4. Create `backend/.env`.
5. Run:

```bash
docker compose up --build -d
```

For public production use, place Nginx/Caddy in front of the backend and enable HTTPS.

## Ollama deployment note

Ollama is best for local/private mode. For a public hosted app, either:

- host Ollama on your own VM/GPU instance and set `OLLAMA_BASE_URL`, or
- add cloud fallback providers such as OpenAI, Claude, Gemini, Azure OpenAI, or AWS Bedrock.
