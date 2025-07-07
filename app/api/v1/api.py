from fastapi import APIRouter

from app.api.v1.endpoints import tournaments, auth

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

api_router.include_router(
    tournaments.router,
    prefix="/tournaments",
    tags=["tournaments"]
)

# api_router.include_router(
#     rounds.router,
#     prefix="/rounds",
#     tags=["rounds"]
# )

