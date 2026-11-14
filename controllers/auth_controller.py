from services.auth_service import register, login

class AuthController:
    def register(self, username, password):
        return register(username, password)

    def login(self, username, password):
        return login(username, password)

    def logout(self):
        return None
