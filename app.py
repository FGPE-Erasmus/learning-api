import connexion
import peewee as pw
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

from local_settings import DATABASE as LOCAL_SETTINGS_DATABASE, MAIL, SECRETS


jwt = JWTManager()
ma = Marshmallow()
db = pw.PostgresqlDatabase(
    database=LOCAL_SETTINGS_DATABASE['name'],
    user=LOCAL_SETTINGS_DATABASE['user'],
    password=LOCAL_SETTINGS_DATABASE['password'],
    host=LOCAL_SETTINGS_DATABASE['host'],
    # TODO: port = 213213
)


def create_app():
    connex_app = connexion.FlaskApp(__name__, specification_dir='rest_api/')
    connex_app.add_api('swagger.yaml')

    app = connex_app.app

    # TODO
    app.config['JWT_SECRET_KEY'] = SECRETS['JWT_SECRET_KEY']
    app.config['TOKEN_SECRET_KEY'] = SECRETS['TOKEN_SECRET_KEY']
    app.config['TOKEN_SECURITY_PASSWORD_SALT'] = SECRETS['TOKEN_SECURITY_PASSWORD_SALT']

    CORS(app, resources={r'*': {'origins': '*'}})

    jwt.init_app(app)
    ma.init_app(app)

    return app
