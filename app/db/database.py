import os

from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# core to get local SQL Lite DB
# SQLALCHEMY_DATABASE_URI = 'sqlite:///todosapp.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
INSTANCE_CONNECTION_NAME = settings.INSTANCE_CONNECTION_NAME

connector = Connector()


# Cloud SQL Auth Proxy core
# DATABASE_URL = (
#    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
#    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
# )
# DATABASE_URL = "postgresql://Aneesh:Kunmun123$@127.0.0.1:5432/my-first-postgresql-db"
# engine = create_engine(DATABASE_URL, echo=True)

def getconn():
    print(f'the instance name is : {INSTANCE_CONNECTION_NAME}')
    print(f'the DB_USER name is : {DB_USER}')
    print(f'the DB_PASSWORD name is : {DB_PASSWORD}')
    print(f'the DB_NAME name is : {DB_NAME}')
    return connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
    )


engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    pool_size=5,
    max_overflow=2,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

SessionLocal = sessionmaker(bind=engine)
