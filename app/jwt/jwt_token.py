from app.utils.settings import settings
from app.utils.schema import Token
from app.users.manage_users import validate_password

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from jwt.exceptions import InvalidTokenError

import logging
import json

logging.basicConfig(level=settings.log_level, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jwt/v1")

UserDep = Annotated[dict, Depends(validate_password)]

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.hashing_algo)
    return encoded_jwt

@router.post("/token")
async def login_for_access_token(
            user_data: UserDep,
) -> Token:
    user_data_json = json.loads(user_data.body.decode("utf-8"))
    user = user_data_json["username"]
    if user_data.status_code != 202:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(settings.token_expiry))
    access_token = create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")