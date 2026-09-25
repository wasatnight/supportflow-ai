import os
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_mode: Literal["postgresql", "sqlite"] = "postgresql"

    db_user: str = "supportflow_app"
    db_password: SecretStr = SecretStr("")
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "supportflow_db"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def app_data_directory(self) -> Path:
        local_app_data = os.getenv("LOCALAPPDATA")

        if local_app_data:
            root_directory = Path(local_app_data)
        else:
            root_directory = Path.home() / "AppData" / "Local"

        data_directory = root_directory / "SupportFlowAI"
        data_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return data_directory

    @property
    def sqlite_database_path(self) -> Path:
        return self.app_data_directory / "supportflow.db"


settings = Settings()
