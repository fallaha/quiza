from pydantic import BaseModel

class UserResponse(BaseModel):
    name : str
    email : str