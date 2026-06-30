import logging
from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from config import COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UserRegister
from services.auth_service import register_user, authenticate_user
from routers.auth_docs import REGISTER_DOCS, LOGIN_DOCS, LOGOUT_DOCS

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=True,
        path="/"
    )


@router.post("/register", **REGISTER_DOCS)
async def register(user: UserRegister):
    await register_user(user)
    return {"message": "User registered successfully"}


@router.post("/login", **LOGIN_DOCS)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    access_token = await authenticate_user(form_data.username, form_data.password)
    set_auth_cookie(response, access_token)
    return {"message": "Login successful"}


@router.post("/logout", **LOGOUT_DOCS)
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Logged out successfully"}