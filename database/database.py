from typing import Annotated

from sqlalchemy.orm import DeclarativeBase

from config import cfg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import String

async_engine = create_async_engine(
    url=cfg.db_url,
    echo=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(async_engine)

str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }
