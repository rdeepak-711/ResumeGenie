from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

# Incoming POST request model
class ResumeRequest(BaseModel):
    resume_text: str
    job_description: str

# Full Entry
class ResumeEntry(ResumeRequest):
    score: Optional[float]
    feedback: Optional[str]
    created_at: datetime
    tailored_resume: Optional[str]

class User(BaseModel):
    email: EmailStr
    password: str
    created_at: datetime
    credits: Optional[int]=5

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator("password")
    def password_strength(cls, value):
        if len(value)<6:
            raise ValueError("Password must be at least 6 characters long")
        return value

class Token(BaseModel):
    access_token: str
    token_type: str
    email: EmailStr
    credits: int

class CheckoutRequest(BaseModel):
    plan_type: str
    custom_credits: int = None