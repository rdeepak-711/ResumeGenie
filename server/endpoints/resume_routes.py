from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime
from bson import ObjectId

from models import ResumeRequest, User, ResumeEntry
from db import get_user_collection, get_resume_collection
from utils.dependencies import get_current_user
from utils.resumeHelper import score_resume_with_claude, clean_input_text, is_free_usage, validate_text_limits, FREE_TIER_LIMITS, PAID_TIER_LIMITS

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
        is_paid_user = current_user is not None

        validate_text_limits(resumeText, jobDescription, is_paid_user)
        if needsCredit:
            if not current_user:
                raise HTTPException(
                    status_code=401, 
                    detail={
                        "message": "Login required for content exceeding free tier limits",
                        "limits": FREE_TIER_LIMITS,
                        "current": {
                            "resume_chars": len(resumeText),
                            "jd_chars": len(jobDescription),
                            "total_chars": len(resumeText) + len(jobDescription)
                        }
                    }
                )

            if current_user.credits<1:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "message": "Insufficient credits. Please purchase more to continue.",
                        "current_credits": current_user.credits,
                        "required_credits": 1
                    }
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

        response = await score_resume_with_claude(resumeText, jobDescription)

        if not response.get("success"):
            if needsCredit and current_user:
                userCollection = await get_user_collection()
                await userCollection.update_one(
                    {"email": current_user.email},
                    {"$inc": {"credits": 1}}
                )
            
            raise HTTPException(
                status_code=400, 
                detail=response.get("message", "Resume analysis failed")
            )
 
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

        updated_credits = None
        if current_user:
            userCollection = await get_user_collection()
            updated_user = await userCollection.find_one({"email": current_user.email})
            updated_credits = updated_user.get("credits", 0) if updated_user else 0

        return {
            "success": True,
            "message": saveMsg,
            "data": {
                "score": response["score"],
                "feedback": response["feedback"],
                "tailored_resume": response["tailored_resume"],
                "remaining_credits": updated_credits,
                "credits_used": 1 if needsCredit else 0,
                "tier_used": "paid" if needsCredit else "free"
            }
        }

    except HTTPException:
        raise 

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
    
@router.get("/limits")
async def get_usage_limits(current_user: Optional[User] = Depends(get_current_user)):
    """Get character limits for current user"""
    is_paid_user = current_user is not None
    limits = PAID_TIER_LIMITS if is_paid_user else FREE_TIER_LIMITS
    
    return {
        "success": True,
        "data": {
            "limits": limits,
            "tier": "paid" if is_paid_user else "free",
            "current_credits": current_user.credits if current_user else 0
        }
    }

@router.post("/check-limits")
async def check_content_limits(
    resume_text: str,
    job_description: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Check if content fits within user's limits"""
    try:
        resume_text = clean_input_text(resume_text)
        job_description = clean_input_text(job_description)
        
        is_paid_user = current_user is not None
        is_free = is_free_usage(resume_text, job_description)
        
        resume_chars = len(resume_text)
        jd_chars = len(job_description)
        total_chars = resume_chars + jd_chars
        
        limits = PAID_TIER_LIMITS if is_paid_user else FREE_TIER_LIMITS
        
        return {
            "success": True,
            "data": {
                "within_limits": True,
                "is_free_tier": is_free,
                "credits_required": 0 if is_free else 1,
                "current": {
                    "resume_chars": resume_chars,
                    "jd_chars": jd_chars,
                    "total_chars": total_chars
                },
                "limits": limits,
                "tier": "paid" if is_paid_user else "free"
            }
        }
        
    except HTTPException as e:
        return {
            "success": False,
            "message": e.detail,
            "within_limits": False
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error checking limits: {str(e)}",
            "within_limits": False
        }