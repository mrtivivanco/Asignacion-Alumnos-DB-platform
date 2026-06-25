from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from .db.config import create_db_and_tables, engine
from .routes import authors, books, categories, nationalities
from .utils.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed_demo_data(session)
    yield


app = FastAPI(
    title="Database Course Reference API",
    description="Small FastAPI + SQLModel example for a database course.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(nationalities.router)
app.include_router(categories.router)
app.include_router(authors.router)
app.include_router(books.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Database Course Reference API",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
