from datetime import timedelta
from http import HTTPStatus

from api.schema import LoginSchema, RegisterSchema
from flask import render_template, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_refresh_token_required,
                                jwt_required)
from marshmallow import ValidationError
from playhouse.flask_utils import get_object_or_404
from psql.tables import User
from settings import API
from utils.email import Mail
from utils.token import confirm_token, generate_confirmation_token

email_manager = Mail()


def register():
    json_data = request.json

    try:
        user_data = RegisterSchema().load(json_data)
    except ValidationError as error:
        return {'errors': error.messages}, HTTPStatus.BAD_REQUEST

    try:
        user = User.create(
            username=user_data['username'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )  # NOQA
    except Exception:  # FIXME
        return {}, HTTPStatus.UNPROCESSABLE_ENTITY

    token = generate_confirmation_token(user_data['username'])
    confirm_url = f'{API["confirm_url"]}{token}'
    html = render_template('user/activate.html', confirm_url=confirm_url)  # NOQA
    subject = 'Please confirm your email'  # NOQA
    # email_manager.send_email(user.username, subject, html)
    user.is_active = True
    user.save()

    return {}, HTTPStatus.OK


def login():
    #  FIXME
    #  if not request.is_json:
    #     return jsonify({'msg': 'Missing JSON in request'}), 400

    try:
        user_data = LoginSchema().load(request.json)
    except ValidationError as error:
        return {'errors': error.messages}, HTTPStatus.BAD_REQUEST

    username = user_data['username']
    password = user_data['password']

    if not username or not password:
        return {'errors': 'Missing data in ' +
                'JSON'}, HTTPStatus.UNPROCESSABLE_ENTITY

    user = get_object_or_404(User, (User.username == username))
    if user and user.check_password(password):
        if user.is_active is False:
            return {
                'errors': 'Confirm email'
            }, 462

        token = create_access_token(
            identity=username, expires_delta=timedelta(minutes=120)
        )

        ref_token = create_refresh_token(
            identity=username, expires_delta=timedelta(weeks=1)
        )

        return {
            'accessToken': token,
            'refreshToken': ref_token
        }, HTTPStatus.OK

    return {}, HTTPStatus.NOT_FOUND


@jwt_refresh_token_required
def refresh_token():
    user = get_jwt_identity()

    token = create_access_token(
        identity=user, expires_delta=timedelta(minutes=120))

    ref_token = create_refresh_token(
        identity=user, expires_delta=timedelta(weeks=1))

    return {
        'accessToken': token,
        'refreshToken': ref_token
    }, HTTPStatus.OK


@jwt_required
def logout():
    user = get_jwt_identity()  # NOQA
    # TODO LOGOUT FUNCTION - STORING JWT IN DATABASE

    return {}, HTTPStatus.OK


def confirm_email(token):
    try:
        email = confirm_token(token)
    except Exception:  # FIXME
        return {}, HTTPStatus.BAD_REQUEST

    user = get_object_or_404(User, (User.username == email))

    if user.is_active:
        return {
            'error': 'User is already active'
        }, HTTPStatus.BAD_REQUEST
    else:
        user.is_active = True
        user.save()

    return {}, HTTPStatus.OK
