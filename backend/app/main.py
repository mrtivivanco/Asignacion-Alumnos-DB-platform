from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from .db.config import create_db_and_tables, engine
from .routes import academic
from .utils.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed_demo_data(session)
    yield


app = FastAPI(
    title="Sistema de Asignacion de Pruebas API",
    description="FastAPI + SQLModel para asignar alumnos a pruebas extraordinarias.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(academic.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Sistema de Asignacion de Pruebas API",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
