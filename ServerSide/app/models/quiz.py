from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time, timedelta
from app.models.models import GeneralRespnose
from uuid import UUID
from app.models.user import UserResponse

class QuizCreateRequest(BaseModel):
    name : str
    public : bool = True
    onlynext : Optional[bool] = False
    timing : Optional[bool] = False
    random : Optional[bool] = False
    start_time :Optional[datetime]
    end_time :Optional[datetime]


class QuizResponse (BaseModel):
    uuid : UUID
    name : str
    onlynext : Optional[bool]
    public : Optional[bool]
    timing : Optional[bool]
    random : Optional[bool]
    start_time : Optional[datetime]
    end_time: Optional[datetime]
    teacher_name : Optional[str] = 'unknown'
    question_count : Optional[int] = -1
    start_time_shamsi : Optional[str]
    end_time_shamsi : Optional[str]

class QuizResponseData(GeneralRespnose):
    data : Optional[QuizResponse] = {}

class QuizzesResponseData(GeneralRespnose):
    class GetquizzesResponse(BaseModel):
        quizzes : List[QuizResponse]
    data : Optional[GetquizzesResponse]


class AddParticipantsRequest(BaseModel):
    class _Participant(BaseModel):
        email : str
    participants : List[str]

class ParticipantsResponseData(GeneralRespnose):
    class _Participant(BaseModel):
        email : str
    data : Optional[List[str]]

class AnswerRequest(BaseModel):
    uploded_file_url : Optional[str]
    text_answer : Optional[str]
    option_answer : Optional[int]