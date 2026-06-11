
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate
from security import hashear_password


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=list[UsuarioRead])
async def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.execute(select(models.Usuario)).scalars().all()
    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioRead)
async def obtener_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    usuario = db.get(models.Usuario, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario


@router.post("/", response_model=UsuarioRead, status_code=201)
async def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):

    usuario_email = db.execute(
        select(models.Usuario).where(models.Usuario.email == data.email)
    ).scalar_one_or_none()

    if usuario_email:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    usuario_nombre = db.execute(
        select(models.Usuario).where(models.Usuario.nombre_usuario == data.nombre_usuario)
    ).scalar_one_or_none()

    if usuario_nombre:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    datos = data.model_dump(exclude_none=True)

    password = datos.pop("password")

    nuevo = models.Usuario(
        **datos,
        contrasena_hash=hashear_password(password)
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.patch("/{usuario_id}", response_model=UsuarioRead)
async def actualizar_usuario(
    usuario_id: uuid.UUID,
    data: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    usuario = db.get(models.Usuario, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    datos = data.model_dump(exclude_unset=True)

    if "password" in datos:
        usuario.contrasena_hash = hashear_password(datos.pop("password"))

    for campo, valor in datos.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario


@router.delete("/{usuario_id}", status_code=204)
async def eliminar_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    usuario = db.get(models.Usuario, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()