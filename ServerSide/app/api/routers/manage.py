from fastapi import APIRouter, Depends
from playhouse.shortcuts import model_to_dict
from app.db.models import User, MultipleOption
from app.api.dependencies.authentication import get_current_user
from app.models.models import User_Response
from app.models.models import UsersResponse
from app.models.models import error_response
from app.db.models import Quiz, Question, QuizUsers
from app.models.quiz import QuizCreateRequest, QuizResponseData, AddParticipantsRequest, ParticipantsResponseData
from app.db.sql import database
import uuid
import peewee
from app.models.question import QuestionRequest, QuestionResponseData, QuestionsResponseData, OptionRequest, \
    OptionResponseData, OptionResponsePut
from app.globals.const import QuestionType

router = APIRouter(
    prefix='/manage',
    dependencies=[Depends(get_current_user)]
)


@router.get("/users/me", response_model=User_Response)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return model_to_dict(current_user)


@router.get('/users', response_model=UsersResponse)
def users():
    u = User.select().dicts()
    return {'row': list(u)}


@router.post('/quiz/create', response_model=QuizResponseData)
def quiz_creat(quiz: QuizCreateRequest, current_user: User = Depends(get_current_user)):
    with database.atomic():
        quiz_uuid = uuid.uuid4()
        q = Quiz.create(uuid=quiz_uuid, name=quiz.name,
                        public=quiz.public,
                        onlynext=quiz.onlynext,
                        timing=quiz.timing,
                        random=quiz.random,
                        start_time=quiz.start_time, end_time=quiz.end_time, creator=current_user)
    if q:
        return {'data': model_to_dict(q)}
    else:
        return error_response


@router.get('/quizzes')
def get_quizzes(current_user: User = Depends(get_current_user)):
    qz = current_user.created_quizzes.dicts()
    return {'data': {'quizzes': list(qz)}}


@router.get('/quiz/{uuid}', response_model=QuizResponseData)
def get_quiz(uuid, current_user: User = Depends(get_current_user)):
    try:
        qz = current_user.created_quizzes.select().where(Quiz.uuid == uuid).get()
    except (peewee.DataError, peewee.DoesNotExist):
        return {'code': -1, 'msg': 'invalid uuid'}
    return {'data': model_to_dict(qz)}


@router.delete('/quiz/{uuid}', response_model=QuizResponseData)
def delete_quiz(uuid, current_user: User = Depends(get_current_user)):
    with database.atomic():
        try:
            qz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
            res = qz.delete_instance()
        except (peewee.DoesNotExist, peewee.DataError):
            return {'code': -2, 'msg': 'invalid quiz'}
        if res != 1:
            return error_response
        return {'data': model_to_dict(qz)}


@router.put('/quiz/{uuid}', response_model=QuizResponseData)
def put_quiz(uuid, quiz: QuizCreateRequest, current_user: User = Depends(get_current_user)):
    with database.atomic():
        try:
            qz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
        except (peewee.DoesNotExist, peewee.DataError):
            return {'code': -2, 'msg': 'invalid quiz'}
        if quiz.public == False:
            if QuizUsers.select().where(QuizUsers.quiz == qz).count():
                return {'code':-13,'msg':"you can not private quiz that have participant(s)"}
        qz.public = quiz.public
        qz.onlynext = quiz.onlynext
        qz.timing = quiz.timing
        qz.random = quiz.random
        qz.start_time = quiz.start_time
        qz.end_time = quiz.end_time
        res = qz.save()
        if res != 1:
            return error_response
        return {'data': model_to_dict(qz)}


@router.post('/quiz/{uuid}/question/create', response_model=QuestionResponseData)
def create_quiz_question(uuid, q: QuestionRequest, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}

    if not (
            q.qtype == QuestionType.MultiOption or q.qtype == QuestionType.Textual or q.qtype == QuestionType.FileUpload):
        return {'code': -3, 'msg': 'incorrect qtype'}

    with database.atomic():
        try:
            new_question = Question.create(qtype=q.qtype, text=q.text, quantum=q.quantum, number=q.number,
                                           photo_url=q.photo_url, quiz=quiz)
        except peewee.IntegrityError:
            return {'code': -4, 'msg': 'number is already exists'}
    if new_question:
        return {'data': model_to_dict(new_question)}
    else:
        return error_response


@router.get('/quiz/{uuid}/questions', response_model=QuestionsResponseData)
def get_questions(uuid, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}

    questions = quiz.questions.select().order_by(Question.number).dicts()
    return {'data': {'questions': list(questions)}}


@router.get('/quiz/{uuid}/question/{number}', response_model=QuestionResponseData)
def get_question(uuid, number, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}

    try:
        question = quiz.questions.select().where(Question.number == number).get()
    except peewee.DoesNotExist:
        return {'code': -5, 'msg': "this question number doesn't exist"}
    return {'data': model_to_dict(question)}


@router.put('/quiz/{uuid}/question/{number}', response_model=QuestionResponseData)
def put_question(uuid, number, q: QuestionRequest, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}

    try:
        question = quiz.questions.select().where(Question.number == number).get()
    except peewee.DoesNotExist:
        return {'code': -5, 'msg': "this question number doesn't exist"}

    question.qtype = q.qtype
    question.text = q.text
    question.quantum = q.quantum
    question.number = q.number
    question.photo_url = q.photo_url
    question.save()
    return {'data': model_to_dict(question)}


@router.delete('/quiz/{uuid}/question/{number}', response_model=QuestionResponseData)
def delete_question(uuid, number, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}

    try:
        question = quiz.questions.select().where(Question.number == number).get()
        res = question.delete_instance()
    except peewee.DoesNotExist:
        return {'code': -5, 'msg': "this question number doesn't exist"}
    if res != 1:
        return {}
    return {'data': model_to_dict(question)}


@router.post('/quiz/{uuid}/participants/add', response_model=ParticipantsResponseData)
def add_participant(uuid, participants: AddParticipantsRequest, current_user: User = Depends(get_current_user)):
    added_user = []
    try:
        quiz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}

    if quiz.public:
        return {'code':-12,'msg':'you cant add person to private quiz'}

    for email in participants.participants:
        try:
            user = User.select().where(User.email == email).get()
        except peewee.DoesNotExist:
            pass
        else:
            try:
                with database.atomic():
                    QuizUsers.create(quiz=quiz, user=user)
            except peewee.IntegrityError:
                pass
            else:
                added_user.append(user.email)
    return {'data': added_user}


@router.get('/quiz/{uuid}/participants')
def get_participants(uuid, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.where(Quiz.uuid == uuid).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}

    res = quiz.participant_users.select(QuizUsers.user).dicts()
    return {'data': list(res)}


@router.get('/quiz/{uuid}/question/{number}/options')
def get_multiple_option_of_question(uuid, number, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.select().where(Quiz.uuid == uuid).get()
    except (peewee.DataError, peewee.DoesNotExist):
        return {'code': -1, 'msg': 'invalid quiz'}

    try:
        question = Question.select().where((Question.quiz == quiz) &
                                           (Question.number == number)).get()
    except peewee.DoesNotExist:
        return {'code': -5, 'msg': "this question number doesn't exist"}

    options = MultipleOption.select().where(MultipleOption.question == question)
    return {'data': {'options':
                         [model_to_dict(o) for o in list(options)]
                     }}


@router.post('/quiz/{uuid}/question/{number}/option/add', response_model=OptionResponseData)
def add_to_options(uuid, number: int, option: OptionRequest, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.select().where(Quiz.uuid == uuid).get()
    except (peewee.DataError, peewee.DoesNotExist):
        return {'code': -1, 'msg': 'invalid quiz'}

    try:
        question = Question.select().where((Question.quiz == quiz) &
                                           (Question.number == number)).get()
    except peewee.DoesNotExist:
        return {'code': -5, 'msg': "this question number doesn't exist"}

    if option.number <= 0:
        return {'code': -11, 'msg': "the number should be greater than 0"}

    try:
        with database.atomic():
            option_response = MultipleOption.create(question=question, content=option.content, number=option.number)
    except peewee.IntegrityError:
        return {'code': -10, 'msg': "this number for option used previously."}

    return {'data': model_to_dict(option_response, recurse=False)}


@router.get('/quiz/{uuid}/question/{number}/option/{optionnumber}', response_model=OptionResponseData)
def get_option_of_question(uuid, number: int, optionnumber: int, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.select().where(Quiz.uuid == uuid).get()
    except (peewee.DataError, peewee.DoesNotExist):
        return {'code': -1, 'msg': 'invalid quiz'}

    try:
        question = Question.select().where((Question.quiz == quiz) &
                                           (Question.number == number)).get()
    except peewee.DoesNotExist:
        return {'code': -5, 'msg': "this question number doesn't exist"}

    try:
        option_response = MultipleOption.select().where(
            (MultipleOption.question == question) & (MultipleOption.number == abs(optionnumber))).get()
    except peewee.DoesNotExist:
        return {'code': -11, 'msg': "this number for option is not exist"}

    return {'data': model_to_dict(option_response, recurse=False)}


@router.put('/quiz/{uuid}/question/{number}/option/{option_number}', response_model=OptionResponseData)
def edit_option_of_question(uuid, number: int, option_number: int, option: OptionResponsePut,
                            current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.select().where(Quiz.uuid == uuid).get()
    except (peewee.DataError, peewee.DoesNotExist):
        return {'code': -1, 'msg': 'invalid quiz'}

    try:
        question = Question.select().where((Question.quiz == quiz) &
                                           (Question.number == number)).get()
    except peewee.DoesNotExist:
        return {'code': -5, 'msg': "this question number doesn't exist"}

    try:
        option_response = MultipleOption.select().where(
            (MultipleOption.question == question) & (MultipleOption.number == abs(option_number))).get()
    except peewee.DoesNotExist:
        return {'code': -11, 'msg': "this number for option is not exist"}

    if option.content:
        option_response.content = option.content
    if option.number:
        option_response.number = option.number

    option_response.save()

    return {'data': model_to_dict(option_response, recurse=False)}


@router.delete('/quiz/{uuid}/question/{number}/option/{option_number}', response_model=OptionResponseData)
def edit_option_of_question(uuid, number: int, option_number: int,
                            current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.created_quizzes.select().where(Quiz.uuid == uuid).get()
    except (peewee.DataError, peewee.DoesNotExist):
        return {'code': -1, 'msg': 'invalid quiz'}

    try:
        question = Question.select().where((Question.quiz == quiz) &
                                           (Question.number == number)).get()
    except peewee.DoesNotExist:
        return {'code': -5, 'msg': "this question number doesn't exist"}

    try:
        option_response = MultipleOption.select().where(
            (MultipleOption.question == question) & (MultipleOption.number == abs(option_number))).get()
    except peewee.DoesNotExist:
        return {'code': -11, 'msg': "this number for option is not exist"}

    option_response.delete_instance()

    return {'data': model_to_dict(option_response, recurse=False)}
