from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt

from models import UserCreate, User
from db import get_user_collection
from config import SECRET_KEY
from utils.password import hash_password, verify_password, ALGORITHM

async def addNewUser(user: UserCreate):
    try:
        userCollection = await get_user_collection()

        existingUser = await userCollection.find_one({"email": user.email})
        if existingUser:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashedPassword = await hash_password(user.password)
        userData = User(
            email = user.email,
            password = hashedPassword,
            created_at = datetime.utcnow(),
            credits=5
        ).dict()

        await userCollection.insert_one(userData)

        return {
            "success": True,
            "message": "Added to DB"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

async def checkUser(email, password):
    try:
        userCollection = await get_user_collection()
        userData = await userCollection.find_one({"email": email})

        if not userData:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        user=User(**userData)

        if not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        accessTokenExpires = timedelta(minutes=30)
        accessToken = jwt.encode(
            {
                "sub": user.email,
                "exp": datetime.utcnow() + accessTokenExpires
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return {
            "success": True,
            "accessToken": accessToken,
            "tokenType": "bearer",
            "email": user.email,
            "credits": user.credits,
            "message": "Successfully checked"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }