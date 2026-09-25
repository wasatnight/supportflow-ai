from typing import Any

from sqlalchemy import URL, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base


def create_database_url() -> URL:
    if settings.database_mode == "sqlite":
        return URL.create(
            drivername="sqlite+pysqlite",
            database=str(settings.sqlite_database_path),
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password.get_secret_value(),
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


def create_database_engine() -> Engine:
    database_url = create_database_url()

    if settings.database_mode == "sqlite":
        sqlite_engine = create_engine(
            database_url,
            connect_args={
                "check_same_thread": False,
            },
        )

        @event.listens_for(sqlite_engine, "connect")
        def enable_sqlite_foreign_keys(
            dbapi_connection: Any,
            _: Any,
        ) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return sqlite_engine

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


database_url = create_database_url()
engine = create_database_engine()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def initialize_database() -> None:
    from app.models import SupportMessage, SupportRequest

    _ = (
        SupportMessage,
        SupportRequest,
    )

    Base.metadata.create_all(bind=engine)
