from fastapi import APIRouter, HTTPException, status

from ..crud import authors as author_crud
from ..crud import books as book_crud
from ..crud import categories as category_crud
from ..db.config import SessionDep
from ..db.dto import BookCreate, BookRead


router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookRead])
def list_books(session: SessionDep):
    books = book_crud.list_books(session)
    return book_crud.books_to_read(session, books)


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate, session: SessionDep):
    author = author_crud.get_author(session, book_data.author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    category = category_crud.get_category(session, book_data.category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    book = book_crud.create_book(session, book_data)
    return book_crud.book_to_read(session, book)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: SessionDep):
    book = book_crud.get_book(session, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return book_crud.book_to_read(session, book)
