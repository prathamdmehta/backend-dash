from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def get(db: Session, item_id: int) -> Item | None:
    return db.get(Item, item_id)


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> list[Item]:
    return db.query(Item).offset(skip).limit(limit).all()


def create(db: Session, obj_in: ItemCreate) -> Item:
    db_obj = Item(name=obj_in.name, description=obj_in.description)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: Item, obj_in: ItemUpdate) -> Item:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, item_id: int) -> Item | None:
    db_obj = db.get(Item, item_id)
    if db_obj is not None:
        db.delete(db_obj)
        db.commit()
    return db_obj
