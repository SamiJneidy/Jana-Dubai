from fastapi import HTTPException, status

HTTPException
class InvalidCredentials(HTTPException):
    def __init__(self, detail: str = "Invalid Credentials"):
        self.status_code=status.HTTP_404_NOT_FOUND
        self.detail=detail

class InvalidToken(HTTPException):
    def __init__(self, detail: str = "Invalid Token"):
        self.status_code=status.HTTP_401_UNAUTHORIZED
        self.detail=detail

class ResourceNotFound(HTTPException):
    def __init__(self, detail: str = "Resource Not Found"):
        self.status_code=status.HTTP_404_NOT_FOUND
        self.detail=detail

class ResourceAlreadyInUse(HTTPException):
    def __init__(self, detail: str = "Resource Already In Use"):
        self.status_code=status.HTTP_409_CONFLICT
        self.detail=detail
