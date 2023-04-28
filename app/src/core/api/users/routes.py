import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Body, Depends, Path
from src.core.db import schema, crud, models
from src.core.db.session import get_db
from src.core.auth import get_current_user


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get(
    "/email/{email}",
    status_code=200,
    summary="Get user by email",
    response_model=schema.User,
    responses={
        400: {"description": "User not found"},
        200: {"description": "Returns a user object"},
    },
)
async def user_by_email(email: str, db=Depends(get_db)):
    """
    Retrieve a user by e-mail.
    """
    user = crud.get_user_by_email(db, email)
    if user:
        return user

    raise HTTPException(status_code=404, detail=f"No user found")


@user_router.get(
    "/me",
    summary="Get active user",
    status_code=200,
    response_model=schema.User,
    responses={200: {"description": "Returns a user object"}},
)
async def me(current_user: models.User = Depends(get_current_user)):
    """
    Retrieves current logged in user.
    """

    return current_user

