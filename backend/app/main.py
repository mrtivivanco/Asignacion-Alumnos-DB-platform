from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlmodel import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from .db.config import create_db_and_tables, engine
from .routes import academic, exam_pdfs
from .storage.exam_pdfs import ping_pdf_storage
from .utils.seed import seed_demo_data


OPENAPI_TAGS = [
    {"name": "System", "description": "Service status and API entry points."},
    {"name": "Students", "description": "Student records and student-specific exam assignment lookups."},
    {"name": "Degree Programs", "description": "Academic degree program catalog."},
    {"name": "Student Programs", "description": "Links between students and degree programs."},
    {"name": "Course Sections", "description": "Course section records used by enrollments and exams."},
    {"name": "Course Enrollments", "description": "Student enrollments in course sections."},
    {"name": "Exam Blocks", "description": "Allowed extraordinary exam date and time blocks."},
    {"name": "Exams", "description": "Exam records associated with course sections and blocks."},
    {"name": "Exam PDFs", "description": "PDF upload, download, metadata, and deletion backed by MongoDB GridFS."},
    {"name": "Rooms", "description": "Physical room catalog and capacities."},
    {"name": "Exam Room Assignments", "description": "Room and block reservations for exams."},
    {"name": "Student Exam Assignments", "description": "Student assignment creation, listing, and conflict-aware bulk assignment."},
    {"name": "Assignment Conflicts", "description": "Persisted assignment conflicts generated during assignment attempts."},
]

ERROR_CODES_BY_STATUS = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_413_CONTENT_TOO_LARGE: "payload_too_large",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "validation_error",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_error",
    status.HTTP_503_SERVICE_UNAVAILABLE: "service_unavailable",
}


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
    openapi_tags=OPENAPI_TAGS,
)


def normalize_error_detail(status_code: int, detail):
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        return detail

    error = {
        "code": ERROR_CODES_BY_STATUS.get(status_code, "http_error"),
        "message": detail if isinstance(detail, str) else "Request failed",
    }
    if not isinstance(detail, str):
        error["details"] = detail
    return error


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"detail": normalize_error_detail(exc.status_code, exc.detail)}),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder(
            {
                "detail": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "errors": exc.errors(),
                }
            }
        ),
    )


app.include_router(academic.router)
app.include_router(exam_pdfs.router)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "message": "Sistema de Asignacion de Pruebas API",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["System"])
def ready():
    checks = {"postgres": "ok", "mongo": "ok"}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).scalar_one()
    except Exception:
        checks["postgres"] = "unavailable"

    try:
        ping_pdf_storage()
    except Exception:
        checks["mongo"] = "unavailable"

    if any(value != "ok" for value in checks.values()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "service_unavailable",
                "message": "Service dependencies are unavailable",
                "checks": checks,
            },
        )

    return {"status": "ok", "checks": checks}
