from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from httpx_oauth.clients.google import GoogleOAuth2
from fastapi import Depends

from app.core.config import settings
from app.core.user_manager import get_user_manager
from app.models.user import User

bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET_KEY, lifetime_seconds=settings.JWT_EXPIRE_MINUTES * 60)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, str](get_user_manager, [auth_backend])

google_oauth_client = GoogleOAuth2(
    settings.GOOGLE_CLIENT_ID,
    settings.GOOGLE_CLIENT_SECRET,
)
