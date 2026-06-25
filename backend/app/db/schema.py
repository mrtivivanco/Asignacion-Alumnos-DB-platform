from sqlmodel import Field, Relationship, SQLModel


class Nationality(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=80, unique=True)

    authors: list["Author"] = Relationship(back_populates="nationality")


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=80, unique=True)

    books: list["Book"] = Relationship(back_populates="category")


class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=120)
    nationality_id: int = Field(foreign_key="nationality.id")

    nationality: Nationality | None = Relationship(back_populates="authors")
    books: list["Book"] = Relationship(back_populates="author")


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=2, max_length=160)
    publication_year: int = Field(ge=0, le=2100)
    author_id: int = Field(foreign_key="author.id")
    category_id: int = Field(foreign_key="category.id")

    author: Author | None = Relationship(back_populates="books")
    category: Category | None = Relationship(back_populates="books")
