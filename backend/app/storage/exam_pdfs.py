import os
from datetime import datetime, timezone
from functools import lru_cache

import gridfs
from bson import ObjectId
from bson.errors import InvalidId
from gridfs.errors import NoFile
from pymongo import MongoClient
from pymongo.errors import PyMongoError


PDF_CONTENT_TYPE = "application/pdf"


class PdfStorageError(RuntimeError):
    pass


class InvalidStoredFileId(ValueError):
    pass


class StoredFileNotFound(FileNotFoundError):
    pass


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache
def get_mongo_client() -> MongoClient:
    return MongoClient(require_env("MONGO_URI"), serverSelectionTimeoutMS=5000)


@lru_cache
def get_pdf_database():
    return get_mongo_client()[os.getenv("MONGO_DB", "exam_files")]


@lru_cache
def get_pdf_bucket() -> gridfs.GridFS:
    return gridfs.GridFS(get_pdf_database(), collection=os.getenv("MONGO_GRIDFS_BUCKET", "exam_pdfs"))


def ping_pdf_storage() -> None:
    try:
        get_pdf_database().command("ping")
    except PyMongoError as exc:
        raise PdfStorageError("PDF storage is unavailable") from exc


def to_object_id(file_id: str) -> ObjectId:
    try:
        return ObjectId(file_id)
    except (InvalidId, TypeError) as exc:
        raise InvalidStoredFileId("Invalid MongoDB file id") from exc


def save_exam_pdf(exam_id: int, filename: str, content: bytes) -> str:
    try:
        file_id = get_pdf_bucket().put(
            content,
            filename=filename,
            content_type=PDF_CONTENT_TYPE,
            metadata={
                "exam_id": exam_id,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            },
        )
    except PyMongoError as exc:
        raise PdfStorageError("Could not save PDF to MongoDB") from exc

    return str(file_id)


def get_exam_pdf(file_id: str):
    try:
        return get_pdf_bucket().get(to_object_id(file_id))
    except NoFile as exc:
        raise StoredFileNotFound("PDF file not found") from exc
    except PyMongoError as exc:
        raise PdfStorageError("Could not load PDF from MongoDB") from exc


def delete_exam_pdf(file_id: str) -> bool:
    try:
        get_pdf_bucket().delete(to_object_id(file_id))
    except NoFile:
        return False
    except PyMongoError as exc:
        raise PdfStorageError("Could not delete PDF from MongoDB") from exc

    return True


def iter_pdf_chunks(grid_file, chunk_size: int = 256 * 1024):
    try:
        while chunk := grid_file.read(chunk_size):
            yield chunk
    finally:
        close = getattr(grid_file, "close", None)
        if close is not None:
            close()
