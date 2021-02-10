from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time, timedelta
from uuid import UUID
from app.models.models import GeneralRespnose


class QuestionRequest(BaseModel):
    qtype: int
    text: Optional[str] = ''
    quantum: Optional[int]
    number: int
    photo_url: Optional[str]

class OptionResponsePut(BaseModel):
    content: Optional[str]
    number: Optional[int]


class OptionResponse(BaseModel):
    content: str
    number: int


class OptionResponseData(GeneralRespnose):
    data: Optional[OptionResponse] = {}


class QuestionResponse(BaseModel):
    qtype: int
    text: Optional[str]
    quantum: Optional[int]
    number: int
    photo_url: Optional[str]
    nth : int
    user_start_time : Optional[datetime]
    options : Optional[List[OptionResponse]]


class QuestionsResponseData(GeneralRespnose):
    class QuestionResponseList(BaseModel):
        questions: List[QuestionResponse]

    data: Optional[QuestionResponseList] = {}


class QuestionResponseData(GeneralRespnose):
    data: Optional[QuestionResponse] = {}


class OptionRequest(BaseModel):
    content: str
    number: int


