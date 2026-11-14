from services.auth_service import register, login

class AuthController:
    # 🆕 加上 email 參數並傳給底層的 register 服務
    def register(self, username, password, email):
        return register(username, password, email)

    def login(self, username, password):
        return login(username, password)

    def logout(self):
        return None
