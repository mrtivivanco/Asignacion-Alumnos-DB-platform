from fastapi import APIRouter, HTTPException, status

from ..crud import authors as author_crud
from ..crud import books as book_crud
from ..crud import nationalities as nationality_crud
from ..db.config import SessionDep
from ..db.dto import AuthorCreate, AuthorRead, BookRead


router = APIRouter(prefix="/api/authors", tags=["authors"])


@router.get("", response_model=list[AuthorRead])
def list_authors(session: SessionDep):
    authors = author_crud.list_authors(session)
    return author_crud.authors_to_read(session, authors)


@router.post("", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(author_data: AuthorCreate, session: SessionDep):
    nationality = nationality_crud.get_nationality(session, author_data.nationality_id)
    if nationality is None:
        raise HTTPException(status_code=404, detail="Nationality not found")

    author = author_crud.create_author(session, author_data)
    return author_crud.author_to_read(session, author)


@router.get("/{author_id}/books", response_model=list[BookRead])
def list_books_by_author(author_id: int, session: SessionDep):
    author = author_crud.get_author(session, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    books = book_crud.list_books_by_author(session, author_id)
    return book_crud.books_to_read(session, books)
