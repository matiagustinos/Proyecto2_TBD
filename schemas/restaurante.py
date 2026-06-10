
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RestauranteCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    direccion: str
    telefono: Optional[str] = None
    esta_abierto: bool = True
    costo_envio: float

    dueno_id: uuid.UUID


class RestauranteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    descripcion: Optional[str]
    direccion: str
    telefono: Optional[str]
    esta_abierto: bool
    costo_envio: float

    dueno_id: uuid.UUID


class RestauranteUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    esta_abierto: Optional[bool] = None
    costo_envio: Optional[float] = None

    dueno_id: Optional[uuid.UUID] = None