# Jenkins CI/CD Guide

## Purpose

The Jenkins pipeline validates code quality before deployment.

## Pipeline File

```text
infra/jenkins/Jenkinsfile
```

## Stages

1. **Backend install**
   - creates Python virtual environment
   - installs backend dependencies

2. **Lint**
   - runs Ruff against `backend/app` and `backend/tests`

3. **Security**
   - runs Bandit against backend source code

4. **Tests**
   - runs Pytest with coverage

5. **Frontend build**
   - installs npm dependencies
   - builds React/Vite frontend

## Jenkins Requirements

Install on Jenkins agent:

- Python 3.11+
- Node.js 20.19+ or 22.12+
- npm
- Git

## Setup Steps

1. Push this project to GitHub.
2. In Jenkins, create a new Pipeline job.
3. Select “Pipeline script from SCM”.
4. Choose Git.
5. Add repository URL.
6. Set script path:

```text
infra/jenkins/Jenkinsfile
```

7. Save and run build.

## Future Production Deployment Stages

Add these later:

```text
Docker build
Docker image scan
Push image to ECR/Docker Hub
Deploy backend to EC2/ECS
Deploy frontend to Vercel
Run smoke tests
Notify on Slack/email
```
