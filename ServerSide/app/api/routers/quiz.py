import random
from datetime import datetime
from fastapi import APIRouter, Depends
from app.db.models import User, Quiz, QuizUsers, AnsweredQuestion, Question, MultipleOption
from app.api.dependencies.authentication import get_current_user
from playhouse.shortcuts import model_to_dict
from app.globals.const import QuestionType
from app.models.models import GeneralRespnose
from app.models.quiz import QuizzesResponseData, QuizResponseData, AnswerRequest
from app.models.question import QuestionResponseData
import peewee
from app.db.sql import database

router = APIRouter()


@router.get('/quizzes', response_model=QuizzesResponseData)
def get_quizzes(current_user: User = Depends(get_current_user)):
    quiz_list = Quiz.select().join(QuizUsers, peewee.JOIN.LEFT_OUTER, on=(QuizUsers.quiz == Quiz.uuid)).where(
        (QuizUsers.user == current_user) |
        ((Quiz.public == True) & (QuizUsers.user == None))).order_by(Quiz.start_time.desc())

    quizzes = [model_to_dict(q,extra_attrs=['teacher_name','question_count','start_time_shamsi','end_time_shamsi']) for q in list(quiz_list)]
    return {'data': {'quizzes': quizzes}}


@router.get('/quizzes/private', response_model=QuizzesResponseData)
def get_quizzes(current_user: User = Depends(get_current_user)):
    quizzes = current_user.quizzes.select(QuizUsers.quiz).join(Quiz).where(Quiz.public != True)  # get Private Quiz
    all_quiz = [model_to_dict(q.quiz) for q in list(quizzes)]
    return {'data': {'quizzes': all_quiz}}


@router.get('/quiz/{uuid}', response_model=QuizResponseData)
def get_quiz(uuid, current_user: User = Depends(get_current_user)):
    try:
        quiz = current_user.quizzes.select().where(QuizUsers.quiz == uuid).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}
    return {'data': model_to_dict(quiz.quiz, extra_attrs=['teacher_name','question_count','start_time_shamsi','end_time_shamsi'])}


@router.get('/quiz/{uuid}/questions')
def get_quiz_questions(uuid, current_user: User = Depends(get_current_user)):
    try:
        with database.atomic():
            questions = Quiz.select().join(QuizUsers).where((Quiz.uuid == uuid) & (
                    (QuizUsers.user == current_user) | (Quiz.public == True))).get().questions.select().order_by(
                Question.number)
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}
    return {'data': list(questions.dicts())}


# todo:
# this function should add remaning time of question
# also add multi option

@router.get('/quiz/{uuid}/question/next', response_model=QuestionResponseData)
def get_quiz_nex_questions(uuid, current_user: User = Depends(get_current_user)):
    try:
        with database.atomic():
            quiz = Quiz.select().join(QuizUsers, peewee.JOIN.LEFT_OUTER, on=(QuizUsers.quiz == Quiz.uuid)).where((Quiz.uuid == uuid)&(
            (QuizUsers.user == current_user) |
            ((Quiz.public == True) & (QuizUsers.user == None)))).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}
    # Check Quiz Time
    if quiz.end_time is not None and quiz.end_time < datetime.now():
        return {'code': -8, 'msg': 'this quiz has been finished at {}'.format(quiz.end_time)}

    # Get Number of Questin that user answered it. so we can calculate this question
    # is nth questino
    nth = AnsweredQuestion.select().where((AnsweredQuestion.user == current_user) &
                                          (AnsweredQuestion.quiz == quiz)).count()
    try:
        answ_question = AnsweredQuestion.select().where((AnsweredQuestion.user == current_user) &
                                                        (AnsweredQuestion.quiz == quiz) &
                                                        (AnsweredQuestion.closed == False)).get()
        # if last open question has not any time to answer, so next question
        if not answ_question.remaining_time():
            answ_question.closed = True
            answ_question.save()
            raise peewee.DoesNotExist

    except peewee.DoesNotExist:
        # there is not any open question, so go to next question
        all_not_answ_question = Question.select().join(AnsweredQuestion, peewee.JOIN.FULL).where(
            (Question.quiz == quiz) & (AnsweredQuestion.closed == None)).order_by(Question.number)

        if not all_not_answ_question.exists():
            return {'code':-14,'msg': 'no question remind to answer'}

        if quiz.random:
            question = random.choice(all_not_answ_question)
        else:
            question = all_not_answ_question[0]

        answ_question = AnsweredQuestion.get_or_create(user=current_user,
                                       quiz=quiz,
                                       question=question,
                                       defaults={'start_time': datetime.now()}
                                       )

        data = model_to_dict(question, extra_attrs=['options'] ,recurse=False)
        data['nth'] = nth + 1
        data['user_start_time'] = answ_question[0].start_time
        return {'data': data }

    else:
        data = model_to_dict(answ_question.question,extra_attrs=['options'], recurse=False)
        data['nth'] = nth
        data['user_start_time'] = answ_question.start_time
        return {'data': data}


@router.get('/quiz/{uuid}/question/answered')
def get_answered_questinos(uuid, current_user: User = Depends(get_current_user)):
    try:
        with database.atomic():
            quiz = Quiz.select().join(QuizUsers).where(
                (Quiz.uuid == uuid) & ((QuizUsers.user == current_user) | (Quiz.public == True))).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}
    ans = quiz.answeredquestion_set.select().dicts()
    return {'data': list(ans)}


@router.get('/quiz/{uuid}/question/{number}', response_model=QuestionResponseData)
def get_quiz_questions(uuid, number: int, current_user: User = Depends(get_current_user)):
    try:
        with database.atomic():
            quiz = Quiz.select().join(QuizUsers).where(
                (Quiz.uuid == uuid) & ((QuizUsers.user == current_user) | (Quiz.public == True))).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}
    if quiz.onlynext:
        return {'code': -6, 'msg': 'only next question support.'}
    question = quiz.questions.select().order_by(Question.number).limit(1).offset(abs(number - 1))
    if not len(question):
        return {'code': -7, 'msg': "this question number dose not exist."}
    # Set that user see the question at 'now' time
    AnsweredQuestion.get_or_create(user=current_user,
                                   quiz=quiz,
                                   question=question,
                                   defaults={'start_time': datetime.now()}
                                   )
    return {'data': list(question.dicts())[0]}


# todo:
# this can have not check for answer type
# because maybe we want add combine answering type
# for example a file uploaded with textual answer

@router.post('/quiz/{uuid}/question/{number}/answer', response_model=GeneralRespnose)
def set_answer_of_question(uuid, number: int, answer: AnswerRequest, current_user: User = Depends(get_current_user)):
    try:
        with database.atomic():
            quiz = Quiz.select().join(QuizUsers, peewee.JOIN.LEFT_OUTER, on=(QuizUsers.quiz == Quiz.uuid)).where((Quiz.uuid == uuid)&(
            (QuizUsers.user == current_user) |
            ((Quiz.public == True) & (QuizUsers.user == None)))).get()
    except (peewee.DoesNotExist, peewee.DataError):
        return {'code': -2, 'msg': 'invalid quiz'}

    if quiz.end_time is not None and quiz.end_time < datetime.now():
        return {'code': -8, 'msg': 'this quiz has been finished at {}'.format(quiz.end_time)}

    try:
        question = Question.select().where((Question.quiz == quiz) & (Question.number == number)).get()
    except peewee.DoesNotExist:
        return {'code': -7, 'msg': "this question number dose not exist."}

    try:
        answ_question = AnsweredQuestion.select().where(AnsweredQuestion.quiz == quiz,
                                                        AnsweredQuestion.question == question,
                                                        AnsweredQuestion.user == current_user,
                                                        AnsweredQuestion.closed == False).get()
    except peewee.DoesNotExist:
        return {'code': -9, 'msg': "You cant access this question (closed or not open yet)"}

    if not answ_question.remaining_time():
        # Closed The Question to avoid response again
        answ_question.closed = True
        answ_question.save()
        return {'code': -10, 'msg': "The time to answer this question is over"}

    if question.qtype == QuestionType.MultiOption:
        print(answer)
        if answer.option_answer is not None:
            try:
                selected_option = answer.option_answer = MultipleOption.select().where(
                    (MultipleOption.number == answer.option_answer) &
                    (MultipleOption.question == question)).get()
                answ_question.option_answer = selected_option
            except peewee.DoesNotExist:
                return {'code': -11, 'msg': "this selected option does not exist"}


    if question.qtype == QuestionType.Textual:
        answ_question.text_answer = answer.text_answer
    if question.qtype == QuestionType.FileUpload:
        answ_question.uploded_file_url = answer.uploded_file_url

    # Closed The Question to avoid response again
    answ_question.closed = True
    answ_question.save()

    return {'msg': 'your answer has been saved'}
