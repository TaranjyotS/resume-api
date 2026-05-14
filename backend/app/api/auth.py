from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import create_access_token, hash_password, verify_password, pwd_context
from app.models.entities import User
from app.schemas.dto import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

def _clean_username(username: str) -> str:
    return username.lower().strip().replace(" ", "-")

@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    username = _clean_username(payload.username)
    existing_email_user = db.query(User).filter(User.email == email).first()
    if existing_email_user:
        if verify_password(payload.password, existing_email_user.password_hash):
            return TokenResponse(access_token=create_access_token(str(existing_email_user.id)), username=existing_email_user.username, email=existing_email_user.email)
        raise HTTPException(status_code=409, detail="This email is already linked to an account. Please log in instead.")
    existing_username_user = db.query(User).filter(User.username == username).first()
    if existing_username_user:
        raise HTTPException(status_code=409, detail="This username is already taken.")
    user = User(username=username, email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(str(user.id)), username=user.username, email=user.email)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    identifier = payload.identifier.lower().strip()
    user = db.query(User).filter(or_(User.email == identifier, User.username == identifier)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username/email or password.")
    # Upgrade legacy bcrypt hashes to PBKDF2 after successful login.
    if pwd_context.needs_update(user.password_hash):
        user.password_hash = hash_password(payload.password)
        db.commit()
    return TokenResponse(access_token=create_access_token(str(user.id)), username=user.username, email=user.email)
