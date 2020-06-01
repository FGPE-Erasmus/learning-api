
from flask import abort, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from playhouse.flask_utils import get_object_or_404
from datetime import datetime, timedelta
import datetime

from psql.tables import (
    User,
    UserCourse,
    UserCourseExercise,
    ExerciseNote
)
from rest_api.schema import (
    ExerciseNoteSchema,
    UserSchema,
    UserCourseSchema,
    UserCourseExerciseSchema
)
from utils.fgpe_api import FGPEApi
from local_settings import EXERCISES_MAX_AMOUNT

fgpe_api = FGPEApi()

@jwt_required
def get_user_all():
    role = User.get(User.username == get_jwt_identity()).is_admin
    
    if role is True:
        users = User.select()
        user_schema = UserSchema(many=True)
        return user_schema.jsonify(users), HTTPStatus.OK
    else:
        return {"msg": "Not allowed"}, 403


@jwt_required
def get_user_details():
    role = User.get(User.username == get_jwt_identity()).is_admin
    
    if role is True:
        json_data = request.get_json()
        user_name = json_data.get('userName')
        microsoft_mail = json_data.get('mirosoftMail')

        if microsoft_mail is None:  
            user = get_object_or_404(User, (User.username == user_name))
        else:
            user = get_object_or_404(User, (User.microsoft_mail == microsoft_mail))     

        exercieses = UserCourseExercise.select().join(User).where((User.id == user.id) & (UserCourseExercise.last_answer.is_null(False))).select()
        exercieses_schema = UserCourseExerciseSchema(many=True)  
        return exercieses_schema.jsonify(exercieses), HTTPStatus.OK
    else:
        return {"msg": "Not allowed"}, 403


@jwt_required
def get_user():
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    return UserSchema().jsonify(user), HTTPStatus.OK


@jwt_required
def update_user():
    user = get_object_or_404(User, (User.username == get_jwt_identity()))
    interface_lang = request.json.get('interfaceLang', None)
    ui_color = request.json.get('uiColor', None)
    first_name = request.json.get('first_name', None)
    last_name = request.json.get('last_name', None)
    number_of_attempts = request.json.get('number_of_attempts', None)
    solved_amount = request.json.get('solved_amount', None)
    update_login = request.json.get('logginTime', None)

    if interface_lang is not None:
        user.interface_lang = interface_lang
    if ui_color is not None:
        user.ui_color = ui_color
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if number_of_attempts is not None:
        user.number_of_attempts += 1
    if solved_amount is not None and solved_amount == True:
        user.solved_amount += 1
    if update_login is not None:
        user.last_login = datetime.datetime.now()

    user.save()

    return UserSchema().dump(user), HTTPStatus.OK


@jwt_required
def user_course(platformCourseId: int):
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    user_course = UserCourse.get_or_create(user=user, platform_course_id=platformCourseId)

    return UserCourseSchema().jsonify(user_course[0]), HTTPStatus.CREATED if user_course[1] else HTTPStatus.OK


@jwt_required
def user_courses():
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    courses = UserCourse.select().join(User).where(User.id == user.id).select()
    courses_schema = UserCourseSchema(many=True)

    return courses_schema.jsonify(courses), HTTPStatus.OK


@jwt_required
def set_user_course_position(platformCourseId: int):
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    position_id = request.json.get('platformCourseExerciseId', 0)
    position = get_object_or_404(UserCourseExercise, (UserCourseExercise.platform_course_exercise_id == position_id), (UserCourseExercise.user == user))

    course = UserCourse.select().join(User).where(User.id == user.id, UserCourse.platform_course_id == platformCourseId).get()
    course.position = position
    course.save()

    return UserCourseSchema().jsonify(course), HTTPStatus.OK


@jwt_required
def user_course_exercises():
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    exercieses = UserCourseExercise.select().join(User).where(User.id == user.id).select()
    exercieses_schema = UserCourseExerciseSchema(many=True)

    return exercieses_schema.jsonify(exercieses), HTTPStatus.OK


@jwt_required
def user_course_exercise(platformCourseExerciseId: int, platformCourseId: int):
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    course = UserCourse.get_or_create(user=user, platform_course_id=platformCourseId)[0]

    exercise = UserCourseExercise.get_or_create(course=course, user=user, platform_course_exercise_id=platformCourseExerciseId)
    exercise_schema = UserCourseExerciseSchema()

    return exercise_schema.jsonify(exercise[0]), HTTPStatus.CREATED if exercise[1] else HTTPStatus.OK


@jwt_required
def send_answer(platformCourseExerciseId: int):
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    query = UserCourseExercise.select().join(User).where(User.id == user.id, UserCourseExercise.platform_course_exercise_id == platformCourseExerciseId)
    if not query.exists():
        return {'error': 'Exercise not found'}, HTTPStatus.NOT_FOUND
    exercise = query.get()

    json_data = request.get_json()
    answer = json_data.get('answer')
    exercise.last_answer = answer
    exercise.exercise_name = json_data.get('exerciseName')
    exercise.exercise_description = json_data.get('exerciseDescription')
    exercise.module_name = json_data.get('moduleName')
    exercise.project_name = json_data.get('projectName')
    exercise.number_of_attempts += 1

    is_solved_response = json_data.get('solved') 
    
    if exercise.solved is not True and is_solved_response is True:
        exercise.last_good_answer = answer
        exercise.solved = True
    elif exercise.solved is not True and is_solved_response is False:
        exercise.solved = False
    elif exercise.solved is True and is_solved_response is True:
        exercise.last_good_answer = answer

    exercise.save()

    exercise_schema = UserCourseExerciseSchema()

    return exercise_schema.jsonify(exercise), HTTPStatus.OK


@jwt_required
def update_time(platformCourseExerciseId: int):
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    query = UserCourseExercise.select().join(User).where(User.id == user.id, UserCourseExercise.platform_course_exercise_id == platformCourseExerciseId)
    if not query.exists():
        return {'error': 'Exercise not found'}, HTTPStatus.NOT_FOUND
    exercise = query.get()

    time = request.json['time']
    if time is None:
        return {}, HTTPStatus.NOT_FOUND

    exercise.time_spent_seconds += time
    exercise.save()

    exercise_schema = UserCourseExerciseSchema()

    user.time_spent_seconds += time
    user.save()

    return exercise_schema.jsonify(exercise), HTTPStatus.OK


@jwt_required
def add_note(exerciseId: str):
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    exercise = get_object_or_404(
        UserCourseExercise, (UserCourseExercise.platform_course_exercise_id == exerciseId), (UserCourseExercise.user == user))

    note = request.json['note']

    note = ExerciseNote.create(
        note=note,
        exercise=exercise
    )

    return ExerciseNoteSchema().jsonify(note), HTTPStatus.CREATED


@jwt_required
def save_code(exerciseId: str):
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    exercise = get_object_or_404(
        UserCourseExercise, (UserCourseExercise.platform_course_exercise_id == exerciseId), (UserCourseExercise.user == user))

    code = request.json.get('code')
    if code is None:
        return {}, HTTPStatus.BAD_REQUEST

    exercise.saved_code = code
    exercise.save()

    return UserCourseExerciseSchema().jsonify(exercise), HTTPStatus.OK


@jwt_required
def set_project(projectId: str):
    user = get_object_or_404(User, (User.username == get_jwt_identity()))

    user.selected_project = projectId
    user.save()

    return UserSchema().jsonify(user), HTTPStatus.OK


@jwt_required
def projects():
    return return_result(fgpe_api.get_endpoint('projects')).json()


@jwt_required
def project(projectId: str):
    return return_result(fgpe_api.get_endpoint(f'projects/{projectId}')).json()


@jwt_required
def exercise(id: str):
    return return_result(fgpe_api.get_endpoint(f'exercises/{id}/?join=statements&join=instructions&join=templates&join=skeletons&join=embeddables&join=solutions&join=libraries&join=tests&join=dynamic_correctors&join=static_correctors')).json()


@jwt_required
def exercises(projectId: str):
    return return_result(fgpe_api.get_endpoint(f'exercises?limit={EXERCISES_MAX_AMOUNT}', headers={'project': projectId})).json()


@jwt_required
def chalanges(id: str):
    return return_result(fgpe_api.get_endpoint(f'challenges?filter=gl_id||eq||{id}')).json()


@jwt_required
def dynamic_correctors(pathname: str):
    return return_result(fgpe_api.get_endpoint(f'dynamic-correctors/{pathname}/contents')).text


@jwt_required
def static_correctors(pathname: str):
    return return_result(fgpe_api.get_endpoint(f'static-correctors/{pathname}/contents')).text


@jwt_required
def statements(pathname):
    return return_result(fgpe_api.get_endpoint(f'statements/{pathname}/contents')).text


@jwt_required
def skeletons(pathname):
    return return_result(fgpe_api.get_endpoint(f'skeletons/{pathname}/contents')).text


@jwt_required
def templates(pathname):
    return return_result(fgpe_api.get_endpoint(f'templates/{pathname}/contents')).text


@jwt_required
def libraries(pathname):
    return return_result(fgpe_api.get_endpoint(f'libraries/{pathname}/contents')).json()


@jwt_required
def solutions(pathnameId):
    return return_result(fgpe_api.get_endpoint(f'solutions/{pathnameId}/contents')).text


@jwt_required
def embeddables(pathnameId):
    return return_result(fgpe_api.get_endpoint(f'embeddables/{pathnameId}/contents')).text


@jwt_required
def gamification_layers(projectId):
    return return_result(fgpe_api.get_endpoint(f'gamification-layers/', headers={'Project': projectId})).json()


def return_result(result):
    if result.status_code != 200:
        abort(result.status_code)

    return result
