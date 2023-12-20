import requests

class AuthService:
    SIGN_IN_URL = 'https://gateway.vmod.com/library/customers/sign_in'
    AUTHENTICATE_URL = 'https://gateway.vmod.com/library/customers/me'
    WORKSPACES_URL = 'https://gateway.vmod.com/library/members/all_workspaces'

    def __init__(self):
        self.access_token = None

    def sign_in(self, email: str, password: str) -> None:
        try:
            response = requests.post(AuthService.SIGN_IN_URL, json = { "email": email, "password": password })
            response.raise_for_status()
            self.access_token = response.json()['token']
        except:
            raise Exception('Invalid credentials')
        
    def is_authenticated(self) -> bool:
        try:
            response = requests.get(AuthService.AUTHENTICATE_URL, headers = { 'Authorization': f'Bearer {self.access_token}' })
            response.raise_for_status()
            return True
        except:
            return False
        
    def get_workspaces(self):
        try:
            response = requests.get(AuthService.WORKSPACES_URL, headers = { 'Authorization': f'Bearer {self.access_token}' })
            response.raise_for_status()
            return list(map(lambda x: { "id": x["workspace"]["id"], "name": x["workspace"]["name"] }, filter(lambda x: x["status"] == "active", response.json())))
        except:
            raise Exception('Invalid workspaces')