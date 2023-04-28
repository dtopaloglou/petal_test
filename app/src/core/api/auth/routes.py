from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.auth import (
    JWTBearer,
    create_access_token,
    create_refresh_token,
    authenticate_user,
)
from src.core.db.schema import *

from src.core.db import models
from src.core.db.session import get_db

auth_router = APIRouter(prefix="/auth", tags=["auth"], include_in_schema=False)


@auth_router.post(
    "/login", response_model=Token, summary="Log in with username and password"
)
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """

    Used to authenticate user with a username and a password.

    """
    user: models.User = authenticate_user(db, form_data.username, form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # if the user has specific privileges, add scopes to token creation methods

    token = Token(
        access_token=create_access_token(sub=form_data.username),
        refresh_token=create_refresh_token(sub=form_data.username),
        token_type="Bearer",
    )

    return token


@auth_router.post(
    "/refresh", response_model=AccessToken, summary="Refresh access token"
)
async def refresh(access_token: AccessToken):
    """
    Refresh a valid access token that has expired.
    """

    payload = JWTBearer.verify_token(access_token.access_token)
    user = payload.get("sub")
    access_token = create_access_token(sub=user)
    return AccessToken(access_token=access_token)
