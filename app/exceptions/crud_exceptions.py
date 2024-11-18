class BaseCrudException(Exception):
    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        super().__init__(message, *args, **kwargs)

    def __str__(self):
        return self.message

class LoginError(BaseCrudException):
    def __init__(self, message: str = "Login error."):
        super().__init__(message)

class ResourceNotFound(BaseCrudException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)

class UserNotFound(BaseCrudException):
    def __init__(self, username: str = None, id: int = None):
        self.username = username
        self.id = id
        super().__init__(message=f'User not found. Details: id = {id}, username = {username}')    

class InvalidCredentials(BaseCrudException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)

class TokenExpired(BaseCrudException):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)

class InvalidToken(BaseCrudException):
    def __init__(self, message: str = "Invalid Token"):
        super().__init__(message)