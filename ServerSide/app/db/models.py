from datetime import datetime, timedelta
import peewee as pw
from playhouse.shortcuts import model_to_dict

from app.db.sql import database
from app.globals import calverter

class BaseModelP(pw.Model):
    class Meta:
        database = database


class User(BaseModelP):
    name = pw.CharField()
    password = pw.CharField()
    email = pw.CharField(primary_key=True)
    role = pw.CharField()

    def created_quizzes(self):
        return (self.created_quizzes)

    def quizzes(self):
        return (self.quizzes)


class Quiz(BaseModelP):
    uuid = pw.UUIDField(primary_key=True)
    name = pw.CharField()
    public = pw.BooleanField()
    onlynext = pw.BooleanField()
    timing = pw.BooleanField()
    random = pw.BooleanField()
    start_time = pw.DateTimeField(null=True)
    end_time = pw.DateTimeField(null=True)
    creator = pw.ForeignKeyField(User, backref="created_quizzes")

    def teacher_name(self):
        return self.creator.name

    def question_count(self):
        return Question.select().where(Question.quiz == self).count()

    def start_time_shamsi(self):
        if self.start_time == None:
            return 'نامشخص'
        cal = calverter.Calverter()
        jd = cal.gregorian_to_jd(self.start_time.year, self.start_time.month, self.start_time.day)
        date_shamsi = "/".join([str(i) for i in cal.jd_to_jalali(jd)])
        date_time = str(self.start_time.hour) + ":" + str(self.start_time.minute) + ' ' + date_shamsi
        return date_time

    def end_time_shamsi(self):
        if self.end_time == None:
            return 'نامشخص'

        cal = calverter.Calverter()
        jd = cal.gregorian_to_jd(self.end_time.year, self.end_time.month, self.end_time.day)
        date_shamsi = "/".join([str(i) for i in cal.jd_to_jalali(jd)])
        date_time = str(self.end_time.hour) + ":" + str(self.end_time.minute) + ' ' + date_shamsi
        return date_time


class Question(BaseModelP):
    qtype = pw.SmallIntegerField()
    text = pw.TextField()
    quantum = pw.IntegerField(null=True)
    number = pw.IntegerField()
    photo_url = pw.CharField(null=True)
    quiz = pw.ForeignKeyField(Quiz, backref="questions")

    def options(self):
        options_list = MultipleOption.select().where(MultipleOption.question == self)
        options = [model_to_dict(option,exclude=[MultipleOption.question]) for option in list(options_list)]
        return options


    class Meta:
        indexes = ((('number', 'quiz'), True),)


class MultipleOption(BaseModelP):
    question = pw.ForeignKeyField(Question, backref='multiple_option')
    content = pw.TextField()
    number = pw.SmallIntegerField()

    class Meta:
        indexes = ((('question', 'number'), True),)


class QuizUsers(BaseModelP):
    user = pw.ForeignKeyField(User, backref='quizzes')
    quiz = pw.ForeignKeyField(Quiz, backref="participant_users")

    class Meta:
        indexes = ((('user', 'quiz'), True),)


class AnsweredQuestion(BaseModelP):
    user = pw.ForeignKeyField(User)
    quiz = pw.ForeignKeyField(Quiz)
    question = pw.ForeignKeyField(Question)
    uploded_file_url = pw.CharField(null=True)
    text_answer = pw.TextField(null=True)
    option_answer = pw.ForeignKeyField(MultipleOption, null=True)
    start_time = pw.DateTimeField()
    closed = pw.BooleanField(default=False)

    def remaining_time(self):
        if not self.question.quantum:
            return 1
        remain = (self.start_time + timedelta(seconds=self.question.quantum)) - datetime.now()
        if remain < timedelta(seconds=0):
            return 0
        return remain

    class Meta:
        indexes = ((('user', 'quiz', 'question'), True),)


def create_tables():
    print("creating Tables")
    with database:
        database.create_tables([User, Quiz, Question, MultipleOption, QuizUsers, AnsweredQuestion])


create_tables()
