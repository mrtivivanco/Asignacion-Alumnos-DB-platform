import os
from collections.abc import Generator
from pathlib import Path
from typing import Annotated
from urllib.parse import quote_plus

from fastapi import Depends
from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from . import schema


def load_project_env() -> None:
    for parent in Path(__file__).resolve().parents:
        env_file = parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = quote_plus(require_env("POSTGRES_USER"))
    password = quote_plus(require_env("POSTGRES_PASSWORD"))
    host = require_env("POSTGRES_HOST")
    port = require_env("POSTGRES_PORT")
    database = quote_plus(require_env("POSTGRES_DB"))

    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"


load_project_env()

DATABASE_URL = build_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def create_db_and_tables() -> None:
    # Importing schema registers table metadata before SQLModel creates tables.
    _ = schema
    SQLModel.metadata.create_all(engine)
    apply_schema_migrations()


def apply_schema_migrations() -> None:
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE exams ALTER COLUMN block_id DROP NOT NULL"))
        connection.execute(text("ALTER TABLE course_sections DROP COLUMN IF EXISTS section_code"))


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
