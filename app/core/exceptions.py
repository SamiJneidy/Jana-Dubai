from fastapi import HTTPException, status
from psycopg2 import DatabaseError


class Forbidden(HTTPException):
    def __init__(
        self, detail: str = "You don't have permission to access this resource"
    ):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = detail


class ResourceNotFound(HTTPException):
    def __init__(self, resource_name="Resource"):
        self.resource_name = resource_name
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"{resource_name} not found."
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserNotFound(ResourceNotFound):
    def __init__(self):
        super().__init__(resource_name="User")


class ProductNotFound(ResourceNotFound):
    def __init__(self):
        super().__init__(resource_name="Product")


class ProjectNotFound(ResourceNotFound):
    def __init__(self):
        super().__init__(resource_name="Project")


class CategoryNotFound(ResourceNotFound):
    def __init__(self):
        super().__init__(resource_name="Category")


class QuestionNotFound(ResourceNotFound):
    def __init__(self):
        super().__init__(resource_name="Question")


class InvalidCredentials(HTTPException):
    def __init__(self, detail="Invalid credentials"):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class TokenExpired(HTTPException):
    def __init__(self, detail="Token has expired."):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class InvalidToken(HTTPException):
    def __init__(self, detail="Invalid token."):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class Forbidden(HTTPException):
    def __init__(self, detail="You don't have permission to access this resource."):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class ResourceAlreadyInUse(HTTPException):
    def __init__(self, detail="Resource Already In Use"):
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class UnexpectedError(HTTPException):
    def __init__(
        self,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        cause: str = "Not specified",
    ):
        self.detail = f"An unexpected error has occurred during. Please contact the application adminstartor. Cause: {cause}"
        self.status_code = status_code
        super().__init__(self.detail, self.status_code)
