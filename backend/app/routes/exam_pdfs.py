from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError

from ..crud import academic as crud
from ..db.config import SessionDep
from ..storage.exam_pdfs import (
    InvalidStoredFileId,
    PdfStorageError,
    StoredFileNotFound,
    delete_exam_pdf,
    get_exam_pdf,
    iter_pdf_chunks,
    save_exam_pdf,
)
from ..utils.ids import require_id


router = APIRouter(prefix="/api")

EXAM_PDFS_TAG = "Exam PDFs"

MAX_PDF_BYTES = 10 * 1024 * 1024
ALLOWED_PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf", "application/octet-stream"}


def read_pdf_upload(file: UploadFile) -> bytes:
    if file.content_type and file.content_type not in ALLOWED_PDF_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    if file.filename and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must use a .pdf extension")

    content = file.file.read(MAX_PDF_BYTES + 1)
    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="PDF file is too large",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Invalid PDF file")

    return content


def safe_filename(value: str | None, fallback: str) -> str:
    filename = value or fallback
    return filename.replace('"', "").replace("\r", "").replace("\n", "")


def storage_exception_to_http(exc: Exception) -> HTTPException:
    if isinstance(exc, (InvalidStoredFileId, StoredFileNotFound)):
        return HTTPException(status_code=404, detail="PDF file not found")
    if isinstance(exc, PdfStorageError):
        return HTTPException(status_code=503, detail="PDF storage is unavailable")
    return HTTPException(status_code=500, detail="Unexpected PDF storage error")


@router.post("/exams/{exam_id}/pdf", status_code=status.HTTP_201_CREATED, tags=[EXAM_PDFS_TAG])
def upload_exam_pdf(exam_id: int, session: SessionDep, file: UploadFile = File(...)):
    exam = crud.get_exam(session, exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")

    content = read_pdf_upload(file)
    old_file_id = exam.pdf_file_id
    filename = safe_filename(file.filename, f"exam-{exam_id}.pdf")

    try:
        new_file_id = save_exam_pdf(exam_id, filename, content)
    except Exception as exc:
        raise storage_exception_to_http(exc) from exc

    try:
        exam.pdf_file_id = new_file_id
        session.add(exam)
        session.commit()
        session.refresh(exam)
    except SQLAlchemyError as exc:
        session.rollback()
        try:
            delete_exam_pdf(new_file_id)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Could not attach PDF to exam") from exc

    if old_file_id:
        try:
            delete_exam_pdf(old_file_id)
        except Exception:
            pass

    return {
        "exam_id": require_id(exam.exam_id, "Exam"),
        "pdf_file_id": exam.pdf_file_id,
        "filename": filename,
    }


@router.get("/exams/{exam_id}/pdf", tags=[EXAM_PDFS_TAG])
def download_exam_pdf(exam_id: int, session: SessionDep):
    exam = crud.get_exam(session, exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")

    if not exam.pdf_file_id:
        raise HTTPException(status_code=404, detail="Exam does not have a PDF")

    try:
        grid_file = get_exam_pdf(exam.pdf_file_id)
    except Exception as exc:
        raise storage_exception_to_http(exc) from exc

    filename = safe_filename(getattr(grid_file, "filename", None), f"exam-{exam_id}.pdf")
    return StreamingResponse(
        iter_pdf_chunks(grid_file),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/exams/{exam_id}/pdf/metadata", tags=[EXAM_PDFS_TAG])
def get_exam_pdf_metadata(exam_id: int, session: SessionDep):
    exam = crud.get_exam(session, exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")

    if not exam.pdf_file_id:
        raise HTTPException(status_code=404, detail="Exam does not have a PDF")

    try:
        grid_file = get_exam_pdf(exam.pdf_file_id)
    except Exception as exc:
        raise storage_exception_to_http(exc) from exc

    return {
        "exam_id": require_id(exam.exam_id, "Exam"),
        "pdf_file_id": exam.pdf_file_id,
        "filename": getattr(grid_file, "filename", None),
        "length": getattr(grid_file, "length", None),
        "upload_date": getattr(grid_file, "upload_date", None),
        "metadata": getattr(grid_file, "metadata", None),
    }


@router.delete("/exams/{exam_id}/pdf", tags=[EXAM_PDFS_TAG])
def delete_exam_pdf_route(exam_id: int, session: SessionDep):
    exam = crud.get_exam(session, exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")

    if not exam.pdf_file_id:
        return {"exam_id": exam_id, "deleted": False, "reason": "No PDF attached"}

    file_id = exam.pdf_file_id
    try:
        exam.pdf_file_id = None
        session.add(exam)
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Could not detach PDF from exam") from exc

    try:
        deleted = delete_exam_pdf(file_id)
    except InvalidStoredFileId:
        deleted = False
    except Exception as exc:
        try:
            exam.pdf_file_id = file_id
            session.add(exam)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
        raise storage_exception_to_http(exc) from exc

    return {"exam_id": exam_id, "pdf_file_id": file_id, "deleted": deleted}
