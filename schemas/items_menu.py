# schemas/items_menu.py

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemMenuCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    esta_disponible: bool = True

    restaurante_id: uuid.UUID


class ItemMenuRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    descripcion: Optional[str]
    precio: float
    stock: int
    esta_disponible: bool

    restaurante_id: uuid.UUID


class ItemMenuUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    esta_disponible: Optional[bool] = None

    restaurante_id: Optional[uuid.UUID] = None