import connexion
import peewee
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from local_settings import DATABASE as LOCAL_SETTINGS_DATABASE
from local_settings import SECRETS

jwt = JWTManager()
ma = Marshmallow()
db = peewee.PostgresqlDatabase(
    database=LOCAL_SETTINGS_DATABASE['name'],
    user=LOCAL_SETTINGS_DATABASE['user'],
    password=LOCAL_SETTINGS_DATABASE['password'],
    host=LOCAL_SETTINGS_DATABASE['host'],
    # TODO: port = 213213
)


def create_app():
    connex_app = connexion.FlaskApp(__name__, specification_dir='api/')
    connex_app.add_api('swagger.yaml')

    app = connex_app.app

    app.config['JWT_SECRET_KEY'] = SECRETS['JWT_SECRET_KEY']
    app.config['TOKEN_SECRET_KEY'] = SECRETS['TOKEN_SECRET_KEY']
    app.config['TOKEN_SECURITY_PASSWORD_SALT'] = SECRETS[
        'TOKEN_SECURITY_PASSWORD_SALT']

    CORS(app, resources={r'*': {'origins': '*'}})

    jwt.init_app(app)
    ma.init_app(app)

    return app
