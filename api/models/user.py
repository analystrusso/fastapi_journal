# This provides a model for user attributes, username and hashed password. 

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str # should be hashed


class UserCreate(BaseModel):
    username: str
    password: str
