from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse


class Forbidden(HTTPException):
    def __init__(self, detail="You don't have permission to access this resource"):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class ResourceNotFound(HTTPException):
    def __init__(self, resource_name="Resource"):
        self.resource_name = resource_name
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"{resource_name} not found"
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
    def __init__(self, detail="Token has expired"):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class InvalidToken(HTTPException):
    def __init__(self, detail="Invalid token"):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class ResourceAlreadyInUse(HTTPException):
    def __init__(self, resource_name: str = "Resource"):
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = f"{resource_name} already in use"
        super().__init__(status_code=self.status_code, detail=self.detail)


class UsernameAlreadyInUse(ResourceAlreadyInUse):
    def __init__(self):
        super().__init__(resource_name="Username or email")


async def forbidden_exception_handler(request: Request, exc: Forbidden):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        },
    )

async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFound):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        },
    )
async def resource_already_in_use_exception_handler(request: Request, exc: ResourceAlreadyInUse):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        },
    )

async def invalid_token_exception_handler(request: Request, exc: InvalidToken):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        },
    )

async def token_expired_exception_handler(request: Request, exc: TokenExpired):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        },
    )

async def invalid_credentials_exception_handler(request: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        },
    )

def register_handlers(app: FastAPI):
    app.exception_handler(InvalidCredentials)(invalid_credentials_exception_handler)
    app.exception_handler(TokenExpired)(token_expired_exception_handler)
    app.exception_handler(InvalidToken)(invalid_token_exception_handler) 
    app.exception_handler(ResourceAlreadyInUse)(resource_already_in_use_exception_handler)
    app.exception_handler(ResourceNotFound)(resource_not_found_exception_handler) 
    app.exception_handler(Forbidden)(forbidden_exception_handler)