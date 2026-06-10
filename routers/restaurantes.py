
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas.restaurante import RestauranteCreate, RestauranteRead, RestauranteUpdate


router = APIRouter(prefix="/restaurantes", tags=["Restaurantes"])


@router.get("/", response_model=list[RestauranteRead])
async def listar_restaurantes(db: Session = Depends(get_db)):
    restaurantes = db.execute(select(models.Restaurante)).scalars().all()
    return restaurantes


@router.get("/{restaurante_id}", response_model=RestauranteRead)
async def obtener_restaurante(restaurante_id: uuid.UUID, db: Session = Depends(get_db)):
    restaurante = db.get(models.Restaurante, restaurante_id)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    return restaurante


@router.post("/", response_model=RestauranteRead, status_code=201)
async def crear_restaurante(data: RestauranteCreate, db: Session = Depends(get_db)):

    dueno = db.get(models.Usuario, data.dueno_id)

    if not dueno:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")

    nuevo = models.Restaurante(**data.model_dump(exclude_none=True))

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.patch("/{restaurante_id}", response_model=RestauranteRead)
async def actualizar_restaurante(
    restaurante_id: uuid.UUID,
    data: RestauranteUpdate,
    db: Session = Depends(get_db)
):
    restaurante = db.get(models.Restaurante, restaurante_id)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(restaurante, campo, valor)

    # Si el restaurante se cierra, se desactivan todos sus ítems
    if datos.get("esta_abierto") is False:
        items = db.execute(
            select(models.ItemMenu).where(models.ItemMenu.restaurante_id == restaurante_id)
        ).scalars().all()

        for item in items:
            item.esta_disponible = False

    db.commit()
    db.refresh(restaurante)

    return restaurante


@router.delete("/{restaurante_id}", status_code=204)
async def eliminar_restaurante(restaurante_id: uuid.UUID, db: Session = Depends(get_db)):
    restaurante = db.get(models.Restaurante, restaurante_id)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    db.delete(restaurante)
    db.commit()