from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import NotFoundException
from app.crud import item as crud_item
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemRead, status_code=201)
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    return crud_item.create(db, obj_in=item_in)


@router.get("/", response_model=list[ItemRead])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_item.get_multi(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud_item.get(db, item_id=item_id)
    if item is None:
        raise NotFoundException("Item not found")
    return item


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    item = crud_item.get(db, item_id=item_id)
    if item is None:
        raise NotFoundException("Item not found")
    return crud_item.update(db, db_obj=item, obj_in=item_in)


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = crud_item.remove(db, item_id=item_id)
    if item is None:
        raise NotFoundException("Item not found")
