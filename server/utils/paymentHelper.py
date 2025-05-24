import stripe

from config import STRIPE_SECRET_KEY, FRONTEND_URL

PRESET_PLANS = {
    "basic": {"credits": 5, "price": 3.99},
    "standard": {"credits": 10, "price": 6.99},
    "pro": {"credits": 25, "price": 14.99}
}

CUSTOM_CREDIT_PRICE = 0.60

def get_plan_details(plan_type: str, custom_credits: int = None):
    if plan_type in PRESET_PLANS:
        return {
            "credits": PRESET_PLANS[plan_type]["credits"],
            "amount": (PRESET_PLANS[plan_type]["price"]*100),
            "label": plan_type.capitalize() + "Plan"
        }
    elif plan_type == "custom" and custom_credits and custom_credits >25:
        totalPrice = custom_credits * CUSTOM_CREDIT_PRICE
        return {
            "credits": custom_credits,
            "amount": int(totalPrice*100),
            "label": f"{custom_credits} Custom Credits"
        }
    else:
        raise ValueError("Invalid plan type or custom credits must be > 25")
    
async def create_checkout_session(user_email: str, plan_type: str, custom_credits: int = None):
    try:
        plan = get_plan_details(plan_type, custom_credits)

        session = stripe.checkout.Session.create(
            paymentMethodTypes = ["card", "upi"],
            mode = "payment",
            customerEmail = user_email,
            lineItems = [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": plan["label"]
                        },
                        "unit_amount": plan["amount"]
                    },
                    "quantity": 1
                }
            ],
            metadata = {
                "email": user_email,
                "credits": plan["credits"]
            },
            success_url = f"{FRONTEND_URL}/success",
            cancel_url = f"{FRONTEND_URL}/cancel"
        )

        return {
            "success": True,
            "message": session.url
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }