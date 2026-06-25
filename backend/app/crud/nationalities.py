from sqlmodel import Session, select

from ..db.schema import Nationality


def list_nationalities(session: Session) -> list[Nationality]:
    statement = select(Nationality).order_by(Nationality.name)
    return list(session.exec(statement).all())


def get_nationality(session: Session, nationality_id: int) -> Nationality | None:
    return session.get(Nationality, nationality_id)
