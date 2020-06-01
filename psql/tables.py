import datetime

import peewee
from app import db
from werkzeug.security import check_password_hash, generate_password_hash


class Badge(peewee.Model):
    class Meta:
        database = db

    name = pw.CharField(
        unique=True)


class User(peewee.Model):
    class Meta:
        database = db

    username = peewee.CharField(
        max_length=64,
        null=True,
        unique=True)  # username = email

    password = peewee.CharField(
        null=True)

    is_active = peewee.BooleanField(
        default=False)

    is_admin = peewee.BooleanField(
        default=False)

    first_name = peewee.CharField(
        max_length=64)

    last_name = peewee.CharField(
        max_length=64)

    microsoft_id = peewee.CharField(
        max_length=64,
        null=True,
        unique=True)  # oauth

    microsoft_mail = peewee.CharField(
        max_length=128,
        null=True,
        unique=True)

    interface_lang = peewee.CharField(
        default='en')

    ui_color = peewee.CharField(
        default='white')

    level = peewee.IntegerField(
        default=1)

    points = peewee.IntegerField(
        default=0)

    badges = peewee.ManyToManyField(
        Badge,
        backref='badges')

    time_spent_seconds = peewee.IntegerField(
        default=0)

    number_of_attempts = peewee.IntegerField(
        default=0)

    solved_amount = peewee.IntegerField(
        default=0)

    last_login = peewee.DateTimeField(
        null=True)

    selected_project = peewee.CharField(
        null=True)

    selected_module = peewee.CharField(
        null=True)

    @classmethod
    def create(cls, **query):
        pswd = query.pop('password')
        inst = cls(**query)
        inst.set_password(pswd)
        inst.save(force_insert=True)
        return inst

    @classmethod
    def oauth_create(cls, **query):
        inst = cls(**query)
        inst.save(force_insert=True)

        return inst

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class UserCourse(peewee.Model):
    class Meta:
        database = db

    platform_course_id = peewee.CharField(
        null=False)  # COURSE FROM INTERNET

    position = peewee.DeferredForeignKey(
        'UserCourseExercise',
        null=True)

    user = peewee.ForeignKeyField(
        User,
        null=False)


class UserCourseExercise(peewee.Model):
    class Meta:
        database = db

    course = peewee.ForeignKeyField(
        UserCourse,
        backref='exercises')

    platform_course_exercise_id = peewee.CharField(
        null=False)

    solved = peewee.BooleanField(
        default=False)

    saved_code = peewee.TextField(
        null=True)

    started = peewee.BooleanField(
        default=True)

    last_answer = peewee.TextField(
        null=True)

    last_good_answer = peewee.TextField(
        null=True)

    number_of_attempts = peewee.IntegerField(
        default=0)

    time_spent_seconds = peewee.IntegerField(
        default=0)

    user = peewee.ForeignKeyField(
        User,
        null=False)

    project_name = peewee.TextField(
        null=True)

    module_name = peewee.TextField(
        null=True)

    exercise_name = peewee.TextField(
        null=True)

    exercise_description = peewee.TextField(
        null=True)


class ExerciseNote(peewee.Model):
    class Meta:
        database = db

    exercise = peewee.ForeignKeyField(
        UserCourseExercise,
        backref='notes')

    note = peewee.TextField()

    created_at = peewee.DateTimeField(
        default=datetime.datetime.now)
