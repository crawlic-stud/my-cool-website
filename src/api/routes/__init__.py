from fastapi import APIRouter
from . import jwt_auth


api = APIRouter(prefix="/api")
api.include_router(jwt_auth.router)
