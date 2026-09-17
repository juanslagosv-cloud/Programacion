from __future__ import annotations

import json
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ecodes HR"
    app_env: str = "development"
    database_url: str = "sqlite:///./ecodes.db"
    jwt_secret_key: str = "change-me-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    cors_origins: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            trimmed = value.strip()
            if not trimmed:
                return []
            if trimmed.startswith("["):
                try:
                    parsed = json.loads(trimmed)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in trimmed.split(",") if item.strip()]
        return value

    @property
    def cors_origins_parsed(self) -> List[str]:
        return self.cors_origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
