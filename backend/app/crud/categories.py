from sqlmodel import Session, select

from ..db.schema import Category


def list_categories(session: Session) -> list[Category]:
    statement = select(Category).order_by(Category.name)
    return list(session.exec(statement).all())


def get_category(session: Session, category_id: int) -> Category | None:
    return session.get(Category, category_id)
