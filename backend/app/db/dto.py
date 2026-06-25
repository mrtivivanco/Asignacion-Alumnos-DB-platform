from sqlmodel import Field, SQLModel


class NationalityBase(SQLModel):
    name: str = Field(min_length=2, max_length=80)


class NationalityRead(NationalityBase):
    id: int


class CategoryBase(SQLModel):
    name: str = Field(min_length=2, max_length=80)


class CategoryRead(CategoryBase):
    id: int


class AuthorCreate(SQLModel):
    name: str = Field(min_length=2, max_length=120)
    nationality_id: int


class AuthorRead(SQLModel):
    id: int
    name: str
    nationality_id: int
    nationality: NationalityRead


class BookCreate(SQLModel):
    title: str = Field(min_length=2, max_length=160)
    publication_year: int = Field(ge=0, le=2100)
    author_id: int
    category_id: int


class BookRead(SQLModel):
    id: int
    title: str
    publication_year: int
    author_id: int
    category_id: int
    author: AuthorRead
    category: CategoryRead
