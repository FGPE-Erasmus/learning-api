import sys
from getpass import getpass
from flask import render_template, request
from psql.tables import User
from werkzeug.security import generate_password_hash, check_password_hash
from rest_api.schema import UserSchema

def main(): 
    print('Enter username for a Super User account: ')
    username = input()
    print('Enter first name: ')
    first_name = input()
    print('Enter last name: ')
    last_name = input()
    print('Enter password: ')
    password = getpass()
    assert password == getpass('Password (again):')

    user = User.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        is_active=True,
        is_admin=True,
    )
if __name__ == '__main__':
    sys.exit(main())