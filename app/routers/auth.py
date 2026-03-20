from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import logging

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
logger = logging.getLogger(__name__)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    roles: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/create_user/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    logger.info("create_user_operation_started")
    user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        roles=create_user_request.roles,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    db.add(user_model)
    db.commit()
    logger.info("create_user_operation_ended")
    return {"message": "New user created"}


def authenticate_user(username: str, password: str, db: db_dependency):
    retrieved_user = db.query(Users).filter(Users.username == username).first()
    if not retrieved_user:
        return False
    if not bcrypt_context.verify(password, retrieved_user.hashed_password):
        return False
    return retrieved_user


def create_access_token(username: str, user_id: int, user_role: str):
    payload = {
        "username": username,
        "user_id": user_id,
        "user_role": user_role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token", response_model=Token)
async def log_in_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                  db: db_dependency):
    authenticated_user = authenticate_user(form_data.username, form_data.password, db)
    if not authenticated_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")
    token = create_access_token(authenticated_user.username, authenticated_user.id, authenticated_user.roles)
    return {"access_token": token, "token_type": "bearer"}



# async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
#     try:
#         print(f"inside get_current_user() token : {token} at ")
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get('sub')
#         user_id: int = payload.get('id')
#         user_role: str = payload.get('role')
#         if username is None or user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail="Could not validate user")
#         print(f"inside get_current_user() username: {username}, user_id : {user_id} and user_role : {user_role}")
#         return {"username": username, "user_id": user_id, 'user_role': user_role}
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Could not validate user")
#
