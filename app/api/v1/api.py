from fastapi import APIRouter

from app.api.v1.endpoints import tournaments

api_router = APIRouter()

api_router.include_router(
    tournaments.router,
    prefix="/tournaments",
    tags=["tournaments"]
) 