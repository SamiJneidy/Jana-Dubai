from .auth import router as auth_router
from .categories import router as categories_router
from .products import router as products_router
from .projects import router as projects_router
from .users import router as users_router
from .mail import router as mail_router
from .questions import router as questions_router

routers = [auth_router, categories_router, products_router, projects_router, users_router, mail_router, questions_router]