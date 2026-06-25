from sqlmodel import Session, select

from ..db.dto import AuthorCreate, AuthorRead, NationalityRead
from ..db.schema import Author
from ..utils.ids import require_id
from .nationalities import get_nationality


def list_authors(session: Session) -> list[Author]:
    statement = select(Author).order_by(Author.name)
    return list(session.exec(statement).all())


def get_author(session: Session, author_id: int) -> Author | None:
    return session.get(Author, author_id)


def create_author(session: Session, author_data: AuthorCreate) -> Author:
    author = Author.model_validate(author_data)
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


def author_to_read(session: Session, author: Author) -> AuthorRead:
    nationality = get_nationality(session, author.nationality_id)
    if nationality is None:
        raise ValueError("Author references a nationality that does not exist")

    return AuthorRead(
        id=require_id(author.id, "Author"),
        name=author.name,
        nationality_id=author.nationality_id,
        nationality=NationalityRead.model_validate(nationality),
    )


def authors_to_read(session: Session, authors: list[Author]) -> list[AuthorRead]:
    return [author_to_read(session, author) for author in authors]
