from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import SECRET_KEY
from db import get_user_collection
from models import User
from utils.password import ALGORITHM

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2Scheme)):
    credentialsException = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentialsException
    except JWTError:
        raise credentialsException
    
    userCollection = await get_user_collection()
    user = await userCollection.find_one({"email": email})
    if user is None:
        raise credentialsException
    
    return User(**user)