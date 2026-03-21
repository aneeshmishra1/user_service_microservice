from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
INSTANCE_CONNECTION_NAME = settings.INSTANCE_CONNECTION_NAME

connector = Connector()


def get_conn():
    print(f'the instance name is: {INSTANCE_CONNECTION_NAME}')
    print(f'the DB_USER name is: {DB_USER}')
    print(f'the DB_PASSWORD name is: {DB_PASSWORD}')
    print(f'the DB_NAME name is: {DB_NAME}')
    return connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
    )


engine = create_engine(
    "postgresql+pg8000://",
    creator=get_conn,
    pool_size=5,
    max_overflow=2,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

SessionLocal = sessionmaker(bind=engine)
