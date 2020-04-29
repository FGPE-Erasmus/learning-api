import os
import urllib.parse
import uuid
from datetime import timedelta
from http import HTTPStatus

import adal
import flask
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)
import requests

from playhouse.flask_utils import get_object_or_404

from psql.tables import User
from settings import OAUTH


MS_OAUTH = OAUTH['MICROSOFT']


def microsoft_login():
    params = urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': MS_OAUTH['CLIENT_ID'],
        'redirect_uri': MS_OAUTH['REDIRECT_URI'],
        'resource': MS_OAUTH['RESOURCE']
    })

    return {'url': f"{MS_OAUTH['AUTHORITY_URL']}/oauth2/authorize?{params}"}


def microsoft_callback():
    """Handler for the application's Redirect Uri."""

    code = flask.request.args['code']
    auth_context = adal.AuthenticationContext(MS_OAUTH['AUTHORITY_URL'], api_version=None)
    try:
        token_response = auth_context.acquire_token_with_authorization_code(
            code, MS_OAUTH['REDIRECT_URI'], MS_OAUTH['RESOURCE'], MS_OAUTH['CLIENT_ID'], MS_OAUTH['CLIENT_SECRET'])
    except:
        return {}, HTTPStatus.BAD_REQUEST
    
    headers = {
        'Authorization': f"Bearer {token_response['accessToken']}",
        'User-Agent': 'adal-sample',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'SdkVersion': 'sample-python-adal',
        'return-client-request-id': 'true'
    }

    endpoint = MS_OAUTH['RESOURCE'] + MS_OAUTH['API_VERSION'] + '/me'
    ms_user_data = requests.Session().get(endpoint, headers=headers, stream=False).json()

    user = User.get_or_none(User.microsoft_id == ms_user_data['id'])

    if user is None:
        user = User.oauth_create(
            username=ms_user_data['id'],
            first_name=ms_user_data['displayName'],
            last_name=ms_user_data['displayName'],
            microsoft_mail=ms_user_data['mail'],
            microsoft_id=ms_user_data['id']
        )

    token = create_access_token(
        identity=user.username, expires_delta=timedelta(minutes=120)
    )
    ref_token = create_refresh_token(
        identity=user.username, expires_delta=timedelta(weeks=1)
    )

    response = {
        "accessToken": token,
        "refreshToken": ref_token
    }

    return response, HTTPStatus.OK
