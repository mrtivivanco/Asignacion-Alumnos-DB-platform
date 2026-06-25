from fastapi import APIRouter

from ..crud import categories as category_crud
from ..db.config import SessionDep
from ..db.dto import CategoryRead


router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(session: SessionDep):
    return category_crud.list_categories(session)
