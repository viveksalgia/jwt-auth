from app.utils.settings import settings
from app.utils.schema import Users, Token
from app.users.manage_users import validate_password, get_user_details

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer

from jwt.exceptions import InvalidTokenError

import logging
import json

logging.basicConfig(level=settings.log_level, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jwt/v1")

UserDep = Annotated[dict, Depends(validate_password)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
                                    status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"},
                                )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.hashing_algo])
        logger.info(f"Payload - {payload}") 
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    response = await get_user_details(username)
    logger.info(f"User details response - {response.body.decode('utf-8')}") 
    if response.status_code != 200:
            raise credentials_exception
    return response

async def get_current_active_user(
    current_user: Annotated[Users, Depends(get_current_user)],
):
    if current_user.status_code != 200:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.get("/users/me/", response_model=Users)
async def read_users_me(
    current_user: Annotated[Users, Depends(get_current_active_user)],
):
    return current_user