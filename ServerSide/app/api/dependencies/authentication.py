from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
from jose import JWTError, jwt
from datetime import datetime,timedelta
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from app.db.models import User


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception
    username = payload.get('username')
    if not username:
        raise credentials_exception
    user = User.get(User.email == username)
    return user

