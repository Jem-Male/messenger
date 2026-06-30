# from sqlalchemy import create_engine, text
# import psycopg

# BASE_URL_DATABASE = "postgresql+psycopg://postgres:7473@localhost:1000/messenger"

# engine = create_engine(BASE_URL_DATABASE)

# with engine.connect as con:
    
    
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

BASE_URL_DATABASE = "postgresql+asyncpg://postgres:7473@localhost:1000/messenger"

engine = create_async_engine(BASE_URL_DATABASE, echo = True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass