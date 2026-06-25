from sqlmodel import Session, select

from ..db.dto import BookCreate, BookRead, CategoryRead
from ..db.schema import Book
from ..utils.ids import require_id
from .authors import author_to_read, get_author
from .categories import get_category


def list_books(session: Session) -> list[Book]:
    statement = select(Book).order_by(Book.title)
    return list(session.exec(statement).all())


def list_books_by_author(session: Session, author_id: int) -> list[Book]:
    statement = select(Book).where(Book.author_id == author_id).order_by(Book.title)
    return list(session.exec(statement).all())


def get_book(session: Session, book_id: int) -> Book | None:
    return session.get(Book, book_id)


def create_book(session: Session, book_data: BookCreate) -> Book:
    book = Book.model_validate(book_data)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def book_to_read(session: Session, book: Book) -> BookRead:
    author = get_author(session, book.author_id)
    category = get_category(session, book.category_id)

    if author is None:
        raise ValueError("Book references an author that does not exist")
    if category is None:
        raise ValueError("Book references a category that does not exist")

    return BookRead(
        id=require_id(book.id, "Book"),
        title=book.title,
        publication_year=book.publication_year,
        author_id=book.author_id,
        category_id=book.category_id,
        author=author_to_read(session, author),
        category=CategoryRead.model_validate(category),
    )


def books_to_read(session: Session, books: list[Book]) -> list[BookRead]:
    return [book_to_read(session, book) for book in books]
