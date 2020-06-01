import datetime

import peewee as pw
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Badge(pw.Model):
    name = pw.CharField(unique=True)

    class Meta:
        database = db


class User(pw.Model):
    username = pw.CharField(max_length=64, null=True, unique=True)  # username = email
    password = pw.CharField(null=True)
    is_active = pw.BooleanField(default=False)
    is_admin = pw.BooleanField(default=False)

    first_name = pw.CharField(max_length=64)
    last_name = pw.CharField(max_length=64)

    #OAUTH
    microsoft_id = pw.CharField(max_length=64, null=True, unique=True)
    microsoft_mail = pw.CharField(max_length=128, null=True, unique=True)

    interface_lang = pw.CharField(default='en')
    ui_color = pw.CharField(default='white')
    level = pw.IntegerField(default=1)
    points = pw.IntegerField(default=0)
    badges = pw.ManyToManyField(Badge, backref='badges')
    time_spent_seconds = pw.IntegerField(default=0)
    number_of_attempts = pw.IntegerField(default=0)
    solved_amount = pw.IntegerField(default=0)
    last_login = pw.DateTimeField(null=True)

    selected_project = pw.CharField(null=True)
    selected_module = pw.CharField(null=True)

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

    class Meta:
        database = db


class UserCourse(pw.Model):
    platform_course_id = pw.CharField(null=False)  # COURSE FROM INTERNET
    position = pw.DeferredForeignKey('UserCourseExercise', null=True)
    user = pw.ForeignKeyField(User, null=False)

    class Meta:
        database = db


class UserCourseExercise(pw.Model):
    course = pw.ForeignKeyField(UserCourse, backref='exercises')
    platform_course_exercise_id = pw.CharField(null=False)  # COURSE FROM INTERNET
    solved = pw.BooleanField(default=False)
    saved_code = pw.TextField(null=True)
    started = pw.BooleanField(default=True)
    last_answer = pw.TextField(null=True)
    last_good_answer = pw.TextField(null=True)
    number_of_attempts = pw.IntegerField(default=0)
    time_spent_seconds = pw.IntegerField(default=0)
    user = pw.ForeignKeyField(User, null=False)
    project_name = pw.TextField(null=True)
    module_name = pw.TextField(null=True)
    exercise_name = pw.TextField(null=True)
    exercise_description = pw.TextField(null=True)

    class Meta:
        database = db


class ExerciseNote(pw.Model):
    exercise = pw.ForeignKeyField(UserCourseExercise, backref='notes')
    note = pw.TextField()
    created_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
