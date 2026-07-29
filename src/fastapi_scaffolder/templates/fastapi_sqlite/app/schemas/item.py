from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    name: str
    description: str | None = None


class ItemCreate(ItemBase):
    """Fields accepted when creating a new item."""

    pass


class ItemUpdate(BaseModel):
    """Fields accepted when updating an item — all optional."""

    name: str | None = None
    description: str | None = None


class ItemRead(ItemBase):
    """Fields returned to the client."""

    id: int

    model_config = ConfigDict(from_attributes=True)
