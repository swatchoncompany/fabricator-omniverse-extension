class MockAuthService:
    def __init__(self):
        self.access_token = None

    def sign_in(self, email, password) -> None:
        return "mock_token"
    
    def is_authenticated(self) -> bool:
        return True        

    def get_workspaces(self):
        return [{ "id": 1, "name": "workspace1" }, { "id": 2, "name": "workspace2" }]