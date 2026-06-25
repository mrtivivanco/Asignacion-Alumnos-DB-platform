from fastapi import APIRouter

from ..crud import nationalities as nationality_crud
from ..db.config import SessionDep
from ..db.dto import NationalityRead


router = APIRouter(prefix="/api/nationalities", tags=["nationalities"])


@router.get("", response_model=list[NationalityRead])
def list_nationalities(session: SessionDep):
    return nationality_crud.list_nationalities(session)
