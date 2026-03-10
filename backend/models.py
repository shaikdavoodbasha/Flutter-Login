from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    hashed_password: str


class CreateUser(SQLModel):
    name: str
    email: str
    password: str


class LoginUser(SQLModel):
    email: str
    password: str