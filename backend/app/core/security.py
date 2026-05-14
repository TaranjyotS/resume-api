from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# PBKDF2 avoids bcrypt's 72-byte password limit and works consistently across
# Windows/Python local environments. It is sufficient for this portfolio starter;
# production deployments can move to Argon2id via argon2-cffi when desired.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated=["bcrypt"])

def _normalize_password(password: str) -> str:
    return str(password or "")

def hash_password(password: str) -> str:
    return pwd_context.hash(_normalize_password(password))

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(_normalize_password(password), password_hash)

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=8)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
