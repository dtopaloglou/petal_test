from typing import Optional, Dict, List

import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
    SecurityScopes,
)

import logging
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from src.core.db import session, schema, crud, models
from src.core import security

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scopes={
        "me": "Read information about current user",
        "admin": "CRUD operations on organizations, etc.",
    },
)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # this should be hidden in ENV variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
REFRESH_EXPIRE = 30  # days


class AccessToken(BaseModel):
    access_token: str


class Token(AccessToken):
    access_token: str
    token_type: str
    refresh_token: str


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Dict]:
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            return self.verify_token(credentials.credentials)
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_token(encoded: str) -> Optional[Dict]:
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate client",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                encoded,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_aud": False},
            )

            return payload
        except ExpiredSignatureError:
            logging.error("Token expired")
            raise credentials_exception
        except InvalidSignatureError:
            logging.error("Invalid signature")
            raise credentials_exception
        except DecodeError:
            logging.error("Encoding error")
            raise credentials_exception
        except Exception as e:
            logging.error("Unknown JWT Error: " + str(e))
            raise credentials_exception


async def get_current_user(
    security_scopes: SecurityScopes,
    db=Depends(session.get_db),
    token: str = Depends(security.oauth2_scheme),
) -> models.User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    payload = JWTBearer.verify_token(token)
    email: str = payload.get("sub")
    scopes: List[str] = payload.get("scopes", [])
    user: models.User = crud.get_user_by_email(db, email)

    if not user:
        logging.error(f"Could not find user: {email}")
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


def authenticate_user(db, email: str, password: str) -> models.User:
    user: models.User = crud.get_user_by_email(db, email)
    if user and security.check_password(password, user.password):
        return user


def create_access_token(sub: str, scopes: List[str] = None) -> str:
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=sub,
        scopes=scopes,
    )


def create_refresh_token(sub: str) -> str:
    return _create_token(
        token_type="refresh_token",
        lifetime=timedelta(days=REFRESH_EXPIRE),
        sub=sub,
    )


def _create_token(token_type: str, lifetime: timedelta, sub: str, scopes=None) -> str:
    if scopes is None:
        scopes = []
    payload = {}
    now = datetime.now(tz=timezone.utc)
    expire = now + lifetime
    payload["type"] = token_type
    payload["exp"] = expire
    payload["iat"] = now
    payload["sub"] = sub
    payload["scopes"] = scopes

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
