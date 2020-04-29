from itsdangerous import URLSafeTimedSerializer

from settings import SECRETS


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRETS['TOKEN_SECRET_KEY'])

    return serializer.dumps(email, salt=SECRETS['TOKEN_SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRETS['TOKEN_SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=SECRETS['TOKEN_SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False

    return email
