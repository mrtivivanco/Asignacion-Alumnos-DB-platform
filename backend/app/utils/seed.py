from faker import Faker
from sqlmodel import Session, select

from ..db.schema import Author, Book, Category, Nationality
from .ids import require_id


SEED_VALUE = 2026
NATIONALITY_COUNT = 4
CATEGORY_COUNT = 4
AUTHOR_COUNT = 6
BOOK_COUNT = 12


def make_book_title(fake: Faker) -> str:
    words = fake.words(nb=3)
    return " ".join(word.capitalize() for word in words)


def seed_demo_data(session: Session) -> None:
    """Insert Faker-generated reference data once so repeated starts are safe."""
    existing_book = session.exec(select(Book)).first()
    if existing_book is not None:
        return

    fake = Faker()
    fake.seed_instance(SEED_VALUE)

    nationalities = [
        Nationality(name=fake.unique.country())
        for _ in range(NATIONALITY_COUNT)
    ]
    categories = [
        Category(name=fake.unique.word().title())
        for _ in range(CATEGORY_COUNT)
    ]

    session.add_all([*nationalities, *categories])
    session.commit()

    for item in [*nationalities, *categories]:
        session.refresh(item)

    authors = [
        Author(
            name=fake.unique.name(),
            nationality_id=require_id(
                fake.random_element(elements=nationalities).id,
                "Nationality",
            ),
        )
        for _ in range(AUTHOR_COUNT)
    ]

    session.add_all(authors)
    session.commit()

    for author in authors:
        session.refresh(author)

    books = [
        Book(
            title=make_book_title(fake),
            publication_year=fake.random_int(min=1800, max=2026),
            author_id=require_id(fake.random_element(elements=authors).id, "Author"),
            category_id=require_id(fake.random_element(elements=categories).id, "Category"),
        )
        for _ in range(BOOK_COUNT)
    ]

    session.add_all(books)
    session.commit()
