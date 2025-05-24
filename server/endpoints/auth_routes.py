from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from models import UserCreate, Token, User
from db import get_user_collection
from utils.auth import addNewUser, checkUser
from utils.dependencies import get_current_user
from utils.password import hash_password


router = APIRouter(prefix="/auth", tags = ["AUTH"])

# Me endpoint
@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return {
        "email": user.email,
        "credits": user.credits
    }

# User Signup
@router.post("/signup")
async def signup(user: UserCreate):
    try:
        response = await addNewUser(user=user)
        if not response["success"]:
            raise Exception(response["message"])
        return {
            "success": True,
            "message": "User created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

# User Login
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        response = await checkUser(form_data.username, form_data.password)
        if not response["success"]:
            raise Exception(response["message"])
        return {
            "access_token": response["accessToken"],
            "token_type": response["tokenType"],
            "email": response["email"],
            "credits": response["credits"]
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#Logout endpoint
@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    return {
        "success": True, 
        "message": "Logged out successfully"
    }

@router.get("/profile")
async def get_current_user_data(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "email": current_user.email,
        "credits": current_user.credits,
        "created_at": current_user.created_at
    }

@router.put("/profile")
async def update_user(updates: UserCreate, current_user: User = Depends(get_current_user)):
    try:
        userCollection = await get_user_collection()
        updateData = {}
        if updates.email and updates.email!=current_user.email:
            existingUser = await userCollection.find_one({"email": updates.email})
            if existingUser:
                raise HTTPException(status_code=400, detail="Email already in use")
            updateData["email"] = updates.email
        
        if updates.password:
            hashedPassword = await hash_password(updates.password)
            updateData["password"] = hashedPassword
        
        if not updateData:
            raise Exception("No valid fields to update")
        
        result = await userCollection.update_one(
            {"email": current_user.email},
            {"$set": updateData}
        )

        if result.modified_count == 0:
            raise Exception("update failed or nothing changed")
        
        return {
            "success": False,
            "message": "User updated successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
