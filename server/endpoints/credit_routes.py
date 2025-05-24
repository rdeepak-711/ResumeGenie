from fastapi import APIRouter, status, Depends, HTTPException

from utils.paymentHelper import PRESET_PLANS, CUSTOM_CREDIT_PRICE, create_checkout_session
from utils.dependencies import get_current_user
from models import CheckoutRequest

router = APIRouter(prefix="/credits", tags=["Credits"])

@router.get("/plans")
async def get_credit_plans():
    try:
        plans = []
        for key, value in PRESET_PLANS.items():
            plans.append({
                "plan_type": key,
                "credits": value["credits"],
                "price": value["price"],
                "label": key.capitalize() + "Plan"
            })

        return {
            "success": True,
            "plans": plans,
            "custom_credit_price": CUSTOM_CREDIT_PRICE,
            "custom_credit_note": "Only allowed if purchasing more than 25 credits"
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