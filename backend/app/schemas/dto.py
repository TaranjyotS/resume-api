from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    email: EmailStr
    password: str = Field(min_length=6)

class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, description="Email address or username")
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str | None = None
    email: str | None = None

class CandidateCreate(BaseModel):
    full_name: str = Field(default="Candidate")
    target_role: str = Field(default="Target Role")
    location: str = ""
    resume_text: str = Field(min_length=10)
    skills: str = ""

class JobCreate(BaseModel):
    company: str = ""
    title: str = Field(default="Target Role")
    description: str = Field(min_length=10)
    seniority: str = ""

class TailorRequest(BaseModel):
    candidate_id: int
    job_id: int
    provider: str = "ollama"
    model: str | None = None
    tone: str = "professional, detailed, ATS-friendly"
    create_application_log: bool = True

class ProviderSettings(BaseModel):
    provider: str
    api_key: str | None = None
    model: str | None = None

class ApplicationCreate(BaseModel):
    candidate_id: int
    job_id: int | None = None
    company: str = ""
    title: str = ""
    portal_url: str = ""
    status: str = "draft"
    notes: str = ""

class ApplicationUpdate(BaseModel):
    company: str | None = None
    title: str | None = None
    status: str | None = None
    summary: str | None = None
    notes: str | None = None
    portal_url: str | None = None
