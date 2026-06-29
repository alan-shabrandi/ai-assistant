import logging
from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from config import COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UserRegister

from services.auth_service import register_user, authenticate_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/register")
async def register(user: UserRegister):
    await register_user(user)
    return {"message": "User registered successfully"}


@router.post("/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    access_token = await authenticate_user(form_data.username, form_data.password)
    
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=True,
        path="/"
    )
    return {"message": "Login successful"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Logged out successfully"}