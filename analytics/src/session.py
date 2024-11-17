import enum
import json

from datetime import datetime
from typing import Any, Union
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from contextlib import contextmanager

from settings import settings


def _json_default(obj: Any) -> Union[str, dict]:
    if isinstance(obj, enum.Enum):
        return str(obj)
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            obj = obj.astimezone()
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    raise ValueError(f"Can't serialize {type(obj)}")


def _custom_json_dumps(obj, **kwargs):
    return json.dumps(obj, **kwargs,
                      ensure_ascii=False,
                      allow_nan=False,
                      indent=None,
                      separators=(',', ':'),
                      default=_json_default)


engine = create_engine(
    "{}://{}:{}@{}:{}/{}".format(
        "postgresql",
        settings.DB_USERNAME,
        settings.DB_PASSWORD,
        settings.DB_ADDR,
        settings.DB_PORT,
        settings.DB_NAME,
    ), json_serializer=_custom_json_dumps, pool_size=10, pool_timeout=3
)

_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_database() -> Session:
    db: Session = _session()
    try:
        yield db
        db.flush()
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def with_database():
    db: Session = _session()
    try:
        yield db
        db.flush()
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
