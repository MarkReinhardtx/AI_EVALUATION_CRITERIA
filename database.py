import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


if DATABASE_URL is None:

    raise RuntimeError("В файле .env отсутствует DATABASE_URL")


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(

    bind=engine,
    autoflush=False,
    autocommit=False,
)
class Base(DeclarativeBase):
    pass
