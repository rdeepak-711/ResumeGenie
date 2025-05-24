from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import Optional

from models import ResumeEntry, ResumeRequest, User, CheckoutRequest
from db import get_resume_collection, get_user_collection
from utils.dependencies import get_current_user
from utils.paymentHelper import create_checkout_session

from endpoints.auth_routes import router as auth_router
from endpoints.credit_routes import router as credit_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(credit_router)

# POST request to analyze the resume
@router.post("/analyze")
async def analyzeResume(resume_request: ResumeRequest, current_user: Optional[User] = Depends(get_current_user)):
    try:
        resumeText = clean_input_text(resume_request.resume_text)
        jobDescription = clean_input_text(resume_request.job_description)

        needsCredit = not is_free_usage(resumeText, jobDescription)

        if needsCredit:
            if not current_user:
                raise HTTPException(status_code=401, detail="Login required for longer resumes")

            if current_user.credits<1:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Not enough credits. Please buy more to proceed."
                )
            current_user.credits -= 1

            userCollection = await get_user_collection()
            await userCollection.update_one(
                {"email": current_user.email},
                {"$set": {"credits": current_user.credits}}
            )

        response = await score_resume_with_openai(resumeText, jobDescription)

        if not response.get("success"):
            raise HTTPException(status_code=400, detail=response.get("message", "OpenAI error"))
        
        if current_user:
            resumeEntry = ResumeEntry(
                resume_text=resumeText,
                job_description=jobDescription,
                score=response["score"],
                feedback=response["feedback"],
                tailored_resume=response["tailored_resume"],
                created_at=datetime.utcnow(),
                user_email=current_user.email
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
    
@router.post("/create-checkout-session")
async def create_checkout(request: CheckoutRequest, current_user: dict = Depends(get_current_user)):
    try:
        result = await create_checkout_session(
            user_email=current_user.email,
            plan_type=request.plan_type,
            custom_credits=request.custom_credits
        )

        if result["success"]:
            return {"url": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except ValueError as ve:
         raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error: " + str(e)
        )
    
