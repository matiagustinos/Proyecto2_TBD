# schemas/ordenes.py

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from models import EstadoOrden
from schemas.items_menu import ItemMenuRead


class ItemOrdenCreate(BaseModel):
    item_menu_id: uuid.UUID
    cantidad: int


class ItemOrdenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    item_menu_id: uuid.UUID
    cantidad: int
    precio_unitario: float

    item_menu: Optional[ItemMenuRead] = None


class ItemOrdenUpdate(BaseModel):
    cantidad: Optional[int] = None
    precio_unitario: Optional[float] = None


class OrdenCreate(BaseModel):
    cliente_id: uuid.UUID
    restaurante_id: uuid.UUID
    direccion_entrega: str
    notas: Optional[str] = None

    items: list[ItemOrdenCreate]


class OrdenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    cliente_id: uuid.UUID
    restaurante_id: uuid.UUID
    direccion_entrega: str

    estado: EstadoOrden

    subtotal: float
    costo_envio: float
    descuento: float
    total: float

    notas: Optional[str]

    fecha_creacion: datetime
    fecha_actualizacion: datetime

    items: list[ItemOrdenRead] = None


class OrdenUpdate(BaseModel):
    direccion_entrega: Optional[str] = None
    estado: Optional[EstadoOrden] = None

    subtotal: Optional[float] = None
    costo_envio: Optional[float] = None
    descuento: Optional[float] = None
    total: Optional[float] = None

    notas: Optional[str] = None

    cliente_id: Optional[uuid.UUID] = None
    restaurante_id: Optional[uuid.UUID] = None


class OrdenFiltro(BaseModel):
    estado: Optional[EstadoOrden] = None
    total_minimo: Optional[float] = None
    total_maximo: Optional[float] = None