from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import Optional

from models import ResumeEntry, ResumeRequest, User
from db import get_resume_collection, get_user_collection
from utils.dependencies import get_current_user

from endpoints.auth_routes import router as auth_router
from endpoints.credit_routes import router as credit_router
from endpoints.resume_routes import router as resume_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(credit_router)
router.include_router(resume_router)