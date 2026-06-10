import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Text, 
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from database import Base

# --------- ENUM ---------

class RolUsuario(str, Enum):
    client = "client"
    admin = "admin"
    restaurant_owner = "restaurant_owner"
    restaurant_staff = "restaurant_staff"


class CategoriaCliente(str, Enum):
    sin_categoria = "sin_categoria"
    frecuente = "frecuente"
    premium = "premium"
    vip = "vip"


class EstadoOrden(str, Enum):
    pendiente = "pendiente"
    confirmado = "confirmado"
    preparando = "preparando"
    en_camino = "en_camino"
    entregado = "entregado"

# --------- TABLAS ---------

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nombre_completo = Column(String(100), nullable=False)
    nombre_usuario = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=True)

    contrasena_hash = Column(String(255), nullable=False)

    rol = Column(SQLEnum(RolUsuario), nullable=False, default=RolUsuario.client)

    categoria_cliente = Column(
        SQLEnum(CategoriaCliente),
        nullable=True,
        default=CategoriaCliente.sin_categoria,
    )

    ultimo_acceso = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    restaurantes = relationship("Restaurante", back_populates="dueno")
    ordenes = relationship("Orden", back_populates="cliente")


class Restaurante(Base):
    __tablename__ = "restaurantes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    direccion = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=True)

    esta_abierto = Column(Boolean, default=True)
    costo_envio = Column(Float, nullable=False, default=0)

    dueno_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)

    dueno = relationship("Usuario", back_populates="restaurantes")
    items_menu = relationship("ItemMenu", back_populates="restaurante")
    ordenes = relationship("Orden", back_populates="restaurante")


class ItemMenu(Base):
    __tablename__ = "items_menu"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)

    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    esta_disponible = Column(Boolean, default=True)

    restaurante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("restaurantes.id"),
        nullable=False,
    )

    restaurante = relationship("Restaurante", back_populates="items_menu")
    items_orden = relationship("ItemOrden", back_populates="item_menu")


class Orden(Base):
    __tablename__ = "ordenes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    cliente_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    restaurante_id = Column(UUID(as_uuid=True), ForeignKey("restaurantes.id"), nullable=False)

    direccion_entrega = Column(String(200), nullable=False)

    estado = Column(
        SQLEnum(EstadoOrden),
        nullable=False,
        default=EstadoOrden.pendiente,
    )

    subtotal = Column(Float, nullable=False, default=0)
    costo_envio = Column(Float, nullable=False, default=0)
    descuento = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False, default=0)

    notas = Column(Text, nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    cliente = relationship("Usuario", back_populates="ordenes")
    restaurante = relationship("Restaurante", back_populates="ordenes")
    items = relationship("ItemOrden", back_populates="orden")


class ItemOrden(Base):
    __tablename__ = "items_orden"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    orden_id = Column(UUID(as_uuid=True), ForeignKey("ordenes.id"), nullable=False)
    item_menu_id = Column(UUID(as_uuid=True), ForeignKey("items_menu.id"), nullable=False)

    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)

    orden = relationship("Orden", back_populates="items")
    item_menu = relationship("ItemMenu", back_populates="items_orden")