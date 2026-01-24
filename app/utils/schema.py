from pydantic import BaseModel, Field
from typing import List

class Users(BaseModel):
    user_id: int | None = Field(default=None, description="unique database id for the user")
    user_uuid: str | None = Field(default=None, description="unique id for the user")
    username: str = Field(..., description="User name")
    password: str | None = Field(default=None, description="User Password")
    email_address: str | None = Field(default=None, description="User Email Address")
    first_name: str | None = Field(..., description="User's first name")
    middle_name: str | None = Field(default=None, description="User's middle name")
    last_name: str | None = Field(..., description="User's last name")

class StatusResponse(BaseModel):
    status: str
    datetime: str

class CheckUserName(BaseModel):
    status_code: int
    message: str

class UserCredentials(BaseModel):
    credentials: str = Field(..., description="Base64 encoded credentials")

class UpdateUserCredentials(BaseModel):
    old_credentials: str = Field(..., description="Base64 encoded credentials")
    new_credentials: str = Field(..., description="Base64 encoded credentials")

class Token(BaseModel):
    access_token: str
    token_type: str
