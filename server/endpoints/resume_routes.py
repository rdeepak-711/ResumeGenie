from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime
from bson import ObjectId

from models import ResumeRequest, User, ResumeEntry
from db import get_user_collection, get_resume_collection
from utils.dependencies import get_current_user
from utils.resumeHelper import clean_input_text, is_free_usage, score_resume_with_openai

router = APIRouter(prefix="/resume", tags=["Resume"])

# POST request to analyze the resume
@router.post("/analyze")
async def analyzeResume(
    resume_request: ResumeRequest, 
    current_user: Optional[User] = Depends(get_current_user)
):
    try:
        resumeText = clean_input_text(resume_request.resume_text)
        jobDescription = clean_input_text(resume_request.job_description)

        if not resumeText or not jobDescription:
            raise HTTPException(status_code = 400, detail = "Resume and Job Description cannot be empty")

        needsCredit = not is_free_usage(resumeText, jobDescription)

        if needsCredit:
            if not current_user:
                raise HTTPException(status_code=401, detail="Login required for longer resumes")

            if current_user.credits<1:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Not enough credits. Please buy more to proceed."
                )
            userCollection = await get_user_collection()
            result = await userCollection.update_one(
                {"email": current_user.email, "credits": {"$gte":1}},
                {"$inc": {"credits": -1}}
            )
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=500,
                    detail = "Credit deduction failed. Please try again"
                )

        response = await score_resume_with_openai(resumeText, jobDescription)

        if not response.get("success"):
            raise HTTPException(status_code=400, detail=response.get("message", "OpenAI error"))
 
        if current_user:
            resumeEntry = ResumeEntry(
                user_email=current_user.email,
                resume_text=resumeText,
                job_description=jobDescription,
                score=response["score"],
                feedback=response["feedback"],
                tailored_resume=response["tailored_resume"],
                created_at=datetime.utcnow(),
            )
            resumeCollection = await get_resume_collection()
            await resumeCollection.insert_one(resumeEntry.dict())
            saveMsg = "Resume saved to database"
        else:
            saveMsg = "Entry generated but not saved (user not logged in)"

        return {
            "success": True,
            "message": saveMsg,
            "data": {
                "score": response["score"],
                "feedback": response["feedback"],
                "tailored_resume": response["tailored_resume"],
                "remaining_credits": current_user.credits if current_user else None
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    
@router.get("/history")
async def get_resume_history(current_user: Optional[User] = Depends(get_current_user)):
    try:
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="Login required"
            )
        resumeCollection = await get_resume_collection()
        historyCursor = resumeCollection.find({
            "user_email": current_user.email
        }).sort("created_at", -1)

        history = []

        async for item in historyCursor:
            item["_id"] = str(item["_id"])
            history.append(item)

        return {
            "success": True,
            "count": len(history),
            "data": history,
            "message": "All resumes retrieved"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    
@router.get("/{id}")
async def get_resume_entry(id: str, current_user: User = Depends(get_current_user)):
    resumeCollection = await get_resume_collection()

    try:
        resume = await resumeCollection.find_one({
            "_id": ObjectId(id),
            "user_email": current_user.email
        })

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Resume Entry not found"
            )
        
        resume["_id"] = str(resume["_id"])
        if isinstance(resume["created_at"], datetime):
            resume["created_at"] = resume["created_at"].isoformat()

        return {
            "success": True,
            "data": resume,
            "message": "Resume retrieved"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }