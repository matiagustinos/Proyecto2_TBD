# routers/ordenes.py

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas.ordenes import OrdenCreate, OrdenRead, OrdenUpdate


router = APIRouter(prefix="/ordenes", tags=["Ordenes"])


@router.get("/", response_model=list[OrdenRead])
async def listar_ordenes(db: Session = Depends(get_db)):
    ordenes = db.execute(select(models.Orden)).scalars().all()
    return ordenes


@router.get("/{orden_id}", response_model=OrdenRead)
async def obtener_orden(orden_id: uuid.UUID, db: Session = Depends(get_db)):
    orden = db.get(models.Orden, orden_id)

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    return orden


@router.post("/", response_model=OrdenRead, status_code=201)
async def crear_orden(data: OrdenCreate, db: Session = Depends(get_db)):

    cliente = db.get(models.Usuario, data.cliente_id)

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    restaurante = db.get(models.Restaurante, data.restaurante_id)

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    if not restaurante.esta_abierto:
        raise HTTPException(status_code=400, detail="El restaurante está cerrado")

    if not data.items:
        raise HTTPException(status_code=400, detail="La orden debe tener al menos un ítem")

    subtotal = 0
    items_para_guardar = []

    for item_data in data.items:
        item_menu = db.get(models.ItemMenu, item_data.item_menu_id)

        if not item_menu:
            raise HTTPException(status_code=404, detail="Ítem del menú no encontrado")

        if item_menu.restaurante_id != data.restaurante_id:
            raise HTTPException(
                status_code=400,
                detail="El ítem no pertenece al restaurante seleccionado"
            )

        if not item_menu.esta_disponible:
            raise HTTPException(
                status_code=400,
                detail=f"El ítem {item_menu.nombre} no está disponible"
            )

        if item_menu.stock < item_data.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {item_menu.nombre}"
            )

        subtotal += item_menu.precio * item_data.cantidad

        items_para_guardar.append({
            "item_menu": item_menu,
            "cantidad": item_data.cantidad,
            "precio_unitario": item_menu.precio
        })

    porcentaje_descuento = 0

    if cliente.categoria_cliente == models.CategoriaCliente.frecuente:
        porcentaje_descuento = 0.05
    elif cliente.categoria_cliente == models.CategoriaCliente.premium:
        porcentaje_descuento = 0.10
    elif cliente.categoria_cliente == models.CategoriaCliente.vip:
        porcentaje_descuento = 0.15

    descuento = subtotal * porcentaje_descuento
    costo_envio = restaurante.costo_envio
    total = subtotal + costo_envio - descuento

    nueva_orden = models.Orden(
        cliente_id=data.cliente_id,
        restaurante_id=data.restaurante_id,
        direccion_entrega=data.direccion_entrega,
        notas=data.notas,
        subtotal=subtotal,
        costo_envio=costo_envio,
        descuento=descuento,
        total=total,
        estado=models.EstadoOrden.pendiente
    )

    db.add(nueva_orden)
    db.flush()

    for item_guardar in items_para_guardar:
        item_menu = item_guardar["item_menu"]

        nuevo_item_orden = models.ItemOrden(
            orden_id=nueva_orden.id,
            item_menu_id=item_menu.id,
            cantidad=item_guardar["cantidad"],
            precio_unitario=item_guardar["precio_unitario"]
        )

        db.add(nuevo_item_orden)

        item_menu.stock -= item_guardar["cantidad"]

        if item_menu.stock == 0:
            item_menu.esta_disponible = False

    db.commit()
    db.refresh(nueva_orden)

    return nueva_orden


@router.patch("/{orden_id}", response_model=OrdenRead)
async def actualizar_orden(
    orden_id: uuid.UUID,
    data: OrdenUpdate,
    db: Session = Depends(get_db)
):
    orden = db.get(models.Orden, orden_id)

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(orden, campo, valor)

    db.commit()
    db.refresh(orden)

    return orden


@router.patch("/{orden_id}/avanzar-estado", response_model=OrdenRead)
async def avanzar_estado_orden(
    orden_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    orden = db.get(models.Orden, orden_id)

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    flujo_estados = {
        models.EstadoOrden.pendiente: models.EstadoOrden.confirmado,
        models.EstadoOrden.confirmado: models.EstadoOrden.preparando,
        models.EstadoOrden.preparando: models.EstadoOrden.en_camino,
        models.EstadoOrden.en_camino: models.EstadoOrden.entregado,
    }

    if orden.estado == models.EstadoOrden.entregado:
        raise HTTPException(
            status_code=400,
            detail="La orden ya fue entregada y no puede avanzar más"
        )

    orden.estado = flujo_estados[orden.estado]

    db.commit()
    db.refresh(orden)

    return orden


@router.delete("/{orden_id}", status_code=204)
async def eliminar_orden(orden_id: uuid.UUID, db: Session = Depends(get_db)):
    orden = db.get(models.Orden, orden_id)

    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    db.delete(orden)
    db.commit()