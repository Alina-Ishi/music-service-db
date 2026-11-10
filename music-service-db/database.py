import os

from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./music_service.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    # Импорт внутри функции гарантирует, что все таблицы зарегистрированы
    # в SQLModel.metadata до вызова create_all, независимо от порядка импортов.
    import models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)

