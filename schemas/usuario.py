
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from models import RolUsuario, CategoriaCliente


class UsuarioCreate(BaseModel):
    nombre_completo: str
    nombre_usuario: str
    email: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    password: str

    rol: RolUsuario = RolUsuario.client


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre_completo: str
    nombre_usuario: str
    email: str
    telefono: Optional[str]
    direccion: Optional[str]

    rol: RolUsuario
    categoria_cliente: Optional[CategoriaCliente]

    ultimo_acceso: Optional[datetime]
    fecha_creacion: datetime


class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    nombre_usuario: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    password: Optional[str] = None

    rol: Optional[RolUsuario] = None
    categoria_cliente: Optional[CategoriaCliente] = None


class UsuarioLogin(BaseModel):
    nombre_usuario: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    nombre_usuario: Optional[str] = None
    id: Optional[uuid.UUID] = None
    rol: Optional[RolUsuario] = None