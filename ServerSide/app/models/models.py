from pydantic import BaseModel
from typing import List, Optional

error_response = {'code':0,'msg':'error'}

class User_Request(BaseModel):
    name : str
    password : str
    email :str

class GeneralRespnose(BaseModel):
    code : int = 200
    msg : str = 'ok'
    data = {}

class User_Response(BaseModel):
    name : str
    email :str

class UsersResponse(BaseModel):
    row :  List[User_Response]