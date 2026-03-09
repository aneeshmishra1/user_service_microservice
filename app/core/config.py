import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_USER: str = os.environ["DB_USER"]
    DB_PASSWORD: str = os.environ["DB_PASSWORD"]
    DB_NAME: str = os.environ["DB_NAME"]
    INSTANCE_CONNECTION_NAME: str = os.environ["INSTANCE_CONNECTION_NAME"]
    ENV: str = os.environ["ENV"]
    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM = os.environ["ALGORITHM"]
    ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]


settings = Settings()
