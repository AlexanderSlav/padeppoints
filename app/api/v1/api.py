from fastapi import APIRouter

from app.api.v1.endpoints import tournaments, auth, users, players

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Include admin router separately to avoid duplication in Swagger
api_router.include_router(
    users.admin_router,
    prefix="/users",
    # admin_router already has its own tags and dependencies
)

api_router.include_router(
    tournaments.router,
    prefix="/tournaments",
    tags=["tournaments"]
)

api_router.include_router(
    players.router,
    prefix="/players",
    tags=["players"]
)

