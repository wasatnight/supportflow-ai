from pathlib import Path

from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from sqlalchemy import inspect

from app import main as main_module
from app.core.config import Settings
from app.db import database as database_module


def test_sqlite_path_uses_local_app_data(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(tmp_path),
    )

    local_settings = Settings(
        _env_file=None,
        database_mode="sqlite",
    )

    assert local_settings.app_data_directory == (tmp_path / "SupportFlowAI")
    assert local_settings.sqlite_database_path == (
        tmp_path / "SupportFlowAI" / "supportflow.db"
    )


def test_sqlite_engine_creates_schema(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(tmp_path),
    )
    monkeypatch.setattr(
        database_module.settings,
        "database_mode",
        "sqlite",
    )

    database_url = database_module.create_database_url()

    assert database_url.drivername == "sqlite+pysqlite"
    assert database_url.database is not None
    assert database_url.database.endswith("supportflow.db")

    sqlite_engine = database_module.create_database_engine()

    with sqlite_engine.connect() as connection:
        foreign_keys_enabled = connection.exec_driver_sql(
            "PRAGMA foreign_keys"
        ).scalar_one()

    assert foreign_keys_enabled == 1

    monkeypatch.setattr(
        database_module,
        "engine",
        sqlite_engine,
    )

    database_module.initialize_database()

    assert inspect(sqlite_engine).get_table_names() == [
        "support_messages",
        "support_requests",
    ]

    sqlite_engine.dispose()


def test_sqlite_database_initializes_on_startup(
    monkeypatch: MonkeyPatch,
) -> None:
    initialization_calls: list[bool] = []

    monkeypatch.setattr(
        main_module.settings,
        "database_mode",
        "sqlite",
    )
    monkeypatch.setattr(
        main_module,
        "initialize_database",
        lambda: initialization_calls.append(True),
    )

    with TestClient(main_module.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert initialization_calls == [True]
