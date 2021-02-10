from fastapi.security import OAuth2PasswordRequestForm
import peewee
from fastapi import APIRouter,Depends, HTTPException
from app.models.models import User_Request, GeneralRespnose
from app.db.models import User
from passlib.context import CryptContext
from typing import List, Optional
from datetime import timedelta,datetime
from jose import JWTError, jwt
from app.api.dependencies.authentication import SECRET_KEY
from app.api.dependencies.authentication import ALGORITHM
from app.db.sql import database

router = APIRouter(
    prefix='/auth',
)

def get_user_by_email(email):
    try:
        return User.select().where(User.email == email).get()
    except peewee.DoesNotExist:
        raise HTTPException(status_code=401, detail="Incorrect username")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash_content(content):
    return pwd_context.hash(content)

def verify_password(plain_password,password):
    return pwd_context.verify(plain_password,password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=150)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post('/token')
def login(form_data : OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not verify_password(form_data.password,user.password):
        raise HTTPException(status_code=401, detail="Incorrect Password")

    access_token = create_access_token({'username':user.email})
    return {'access_token':access_token,'token_type':'bearer'}


@router.post('/register',response_model=GeneralRespnose)
def register(req:User_Request):
    with database.atomic():
        try:
            newuser = User.create(name=req.name,password=get_hash_content(req.password),email=req.email,role=0)
        except peewee.IntegrityError:
            return {'code':-20,'msg':'email already taken by another person'}
        else:
            if newuser:
                return {'msg':'Successfully Registerd'}
            return {'code':-200,'msg': 'error in register. try again'}