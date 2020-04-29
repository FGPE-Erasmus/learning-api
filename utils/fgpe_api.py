import datetime
import requests

from settings import FGPE


class FGPEApi():
    base_url = FGPE['url']
    token = ''
    refresh_token = ''

    def __init__(self):
        self.email = FGPE['username']
        self.passwd = FGPE['password']
        self.login()

    def get_endpoint(self, endpoint, headers=None):
        url = f'{self.base_url}{endpoint}'
        fgpe_get_headers = self.get_headers()
        if headers is not None:
            fgpe_get_headers.update(headers)

        response = requests.get(url, headers=fgpe_get_headers)
        if response.status_code == 401:
            self.update_auth_data()
            fgpe_get_headers['Authorization'] = f'Bearer {self.token}'

            response = requests.get(url, headers=fgpe_get_headers)

        return response

    def get_headers(self):
        headers = {
            'Authorization': f'Bearer {self.token}',
        }

        return headers

    def token_refresh(self):
        response = requests.post(f'{self.base_url}{FGPE["ENDPOINT_REFRESH_TOKEN"]}', data={'refreshToken': self.refresh_token})
        if response.status_code == 200:
            self.token = response.json().get('accessToken')

        return response

    def login(self):
        login_data = {
            'email': self.email,
            'password': self.passwd
        }

        response = requests.post(f'{self.base_url}{FGPE["ENDPOINT_LOGIN"]}', data=login_data)
        self.token = response.json().get('accessToken')
        self.refresh_token = response.json().get('refreshToken')

        refresh_token_expires_in = response.json().get('refreshTokenExpiresIn')
        self.refresh_token_expires_datetime = datetime.datetime.now() + datetime.timedelta(seconds=refresh_token_expires_in - 1)

        return response

    def update_auth_data(self):
        if datetime.datetime.now() < self.refresh_token_expires_datetime:
            self.token_refresh()
        else:
            self.login().status_code
