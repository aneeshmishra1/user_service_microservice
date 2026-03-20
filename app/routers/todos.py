from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.models import Todos
import logging

from app.schemas.user_schema import CurrentUser
from app.security.jwt_bearer import JWTBearer

logger = logging.getLogger(__name__)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
auth = JWTBearer()


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=500)
    priority: int = Field(0, ge=0, le=5)
    completed: bool


# async def get_current_user(current_user: Annotated[CurrentUser, Depends(auth)]):
#     try:
#         print(f"inside get_current_user() token: {token}")
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         current_user = CurrentUser(user_id=payload.get("user_id"), username=payload.get("username"),
#                                    user_role=payload.get("user_role"), token=token)
#         if current_user.username is None or current_user.user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail="Could not validate user")
#         print(
#             f"inside get_current_user() username: {current_user.username}, "
#             f"user_id: {current_user.user_id}, "
#             f"user_role: {current_user.user_role}, "
#             f"and token: {token}")
#         return current_user
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Could not validate user")


@router.get("/")
async def read_all(db: db_dependency, current_user: CurrentUser = Depends(auth)):
    logger.info("read_all_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    return db.query(Todos).filter(Todos.owner_id == current_user.user_id).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int, current_user: CurrentUser = Depends(auth)):
    logger.info("read_todo_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id) \
        .filter(Todos.owner_id == current_user.user_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')


@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest,
                      current_user: CurrentUser = Depends(auth)):
    logger.info("create_todo_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = Todos(**todo_request.model_dump(), owner_id=current_user.user_id)
    db.add(todo_model)
    db.commit()
    logger.info("create_todo_operation_ended")
    return {"message": "Todo created"}


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,
                      todo_id: int,
                      todo_request: TodoRequest,
                      current_user: CurrentUser = Depends(auth)):
    logger.info("update_todo_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id) \
        .filter(Todos.owner_id == current_user.user_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    db.commit()
    logger.info("update_todo_operation_ended")
    return {"message": "Todo updated"}


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(ge=0),
                      current_user: CurrentUser = Depends(auth)):
    logger.info("delete_todo_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == current_user.user_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    logger.info("delete_todo_operation_ended")
    return {"message": "Todo deleted"}
