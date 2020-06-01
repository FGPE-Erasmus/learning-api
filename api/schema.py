from app import ma
from marshmallow import fields as marshmallow_fields
from marshmallow.validate import Length
from psql.tables import (Badge, ExerciseNote, User, UserCourse,
                         UserCourseExercise)


class BadgeSchema(ma.Schema):
    class Meta:
        model = Badge
        fields = ['name']


class ExerciseNoteSchema(ma.Schema):
    class Meta:
        model = ExerciseNote
        fields = [
            'note',
            'created_at'
        ]


class LoginSchema(ma.Schema):
    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]


class RegisterSchema(ma.Schema):
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'first_name',
            'last_name'
        ]

    username = marshmallow_fields.Email(
        required=True)

    password = marshmallow_fields.Str(
        validate=Length(min=8, max=64), required=True
    )


class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = [
            'id',
            'badges',
            'first_name',
            'last_name',
            'level',
            'interface_lang',
            'points',
            'selected_project',
            'time_spent_seconds',
            'username',
            'ui_color',
            'is_admin',
            'number_of_attempts',
            'solved_amount',
            'last_login',
            'microsoft_mail',
        ]

    badges = ma.Nested(
        BadgeSchema(many=True))


class UserCourseExerciseSchema(ma.Schema):
    class Meta:
        model = UserCourseExercise
        fields = [
            'platform_course_exercise_id',
            'solved',
            'started',
            'last_answer',
            'last_good_answer',
            'number_of_attempts',
            'time_spent_seconds',
            'notes',
            'saved_code',
            'project_name',
            'module_name',
            'exercise_name',
            'exercise_description',
        ]

    notes = ma.Nested(
        ExerciseNoteSchema(many=True))


class UserCourseExerciseBasicSchema(ma.Schema):
    class Meta:
        model = UserCourseExercise
        fields = [
            'platform_course_exercise_id',
            'solved',
            'started'
        ]


class UserCourseSchema(ma.Schema):
    class Meta:
        model = UserCourse
        fields = [
            'platform_course_id',
            'position',
            'exercises'
        ]

    position = ma.Nested(
        UserCourseExerciseSchema())

    exercises = ma.Nested(
        UserCourseExerciseBasicSchema(many=True))
