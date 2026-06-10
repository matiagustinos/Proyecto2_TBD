
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas.items_menu import ItemMenuCreate, ItemMenuRead, ItemMenuUpdate


router = APIRouter(prefix="/items-menu", tags=["Items del menú"])


@router.get("/", response_model=list[ItemMenuRead])
async def listar_items_menu(db: Session = Depends(get_db)):
    items = db.execute(select(models.ItemMenu)).scalars().all()
    return items


@router.get("/{item_id}", response_model=ItemMenuRead)
async def obtener_item_menu(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(models.ItemMenu, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Ítem del menú no encontrado")

    return item


@router.get("/restaurante/{restaurante_id}", response_model=list[ItemMenuRead])
async def listar_items_por_restaurante(
    restaurante_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    restaurante = db.get(models.Restaurante, restaurante_id)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    items = db.execute(
        select(models.ItemMenu).where(models.ItemMenu.restaurante_id == restaurante_id)
    ).scalars().all()

    return items


@router.post("/", response_model=ItemMenuRead, status_code=201)
async def crear_item_menu(data: ItemMenuCreate, db: Session = Depends(get_db)):

    restaurante = db.get(models.Restaurante, data.restaurante_id)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    datos = data.model_dump(exclude_none=True)

    if datos["stock"] == 0:
        datos["esta_disponible"] = False

    nuevo = models.ItemMenu(**datos)

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.patch("/{item_id}", response_model=ItemMenuRead)
async def actualizar_item_menu(
    item_id: uuid.UUID,
    data: ItemMenuUpdate,
    db: Session = Depends(get_db)
):
    item = db.get(models.ItemMenu, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Ítem del menú no encontrado")

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(item, campo, valor)

    if item.stock == 0:
        item.esta_disponible = False

    db.commit()
    db.refresh(item)

    return item


@router.delete("/{item_id}", status_code=204)
async def eliminar_item_menu(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(models.ItemMenu, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Ítem del menú no encontrado")

    db.delete(item)
    db.commit()