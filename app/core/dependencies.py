from .database import get_db
from fastapi import Depends
from ..crud.auth import (
    get_current_admin,
    get_current_token,
    get_current_user,
    oauth2_scheme
)