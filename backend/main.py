from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager
from typing import Annotated
from passlib.context import CryptContext
from models import User, CreateUser, LoginUser


# DATABASE
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, echo=True)


# CREATE TABLES ON STARTUP
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


# SESSION DEPENDENCY
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# PASSWORD HASHING
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ROOT API
@app.get("/")
def home():
    return {"message": "FastAPI backend running"}


# REGISTER API
@app.post("/register")
def register(session: SessionDep, user_data: CreateUser):

    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_pwd = hash_password(user_data.password)

    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_pwd
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": "User registered successfully"}


# LOGIN API
@app.post("/login")
def login(session: SessionDep, login_user: LoginUser):

    user = session.exec(
        select(User).where(User.email == login_user.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    if not verify_password(login_user.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    return {"message": "Login successful"}