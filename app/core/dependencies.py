from fastapi import Depends

from app.core.auth import fastapi_users
from app.models.user import User

get_current_user = fastapi_users.current_user(active=True)
get_current_superuser = fastapi_users.current_user(active=True, superuser=True)
get_optional_current_user = fastapi_users.current_user(optional=True)
get_current_verified_user = fastapi_users.current_user(active=True, verified=True)
