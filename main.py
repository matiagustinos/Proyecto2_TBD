# main.py

from fastapi import FastAPI

from database import Base, engine
import models

from routers import usuarios
# from routers import restaurantes
# from routers import items_menu
# from routers import ordenes


app = FastAPI(
    title="API Plataforma de Comida",
    description="Proyecto 2 - API REST para plataforma de venta de comida",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


@app.get("/")
def inicio():
    return {"mensaje": "API funcionando correctamente"}


# ROUTERS
app.include_router(usuarios.router)
# app.include_router(restaurantes.router)
# app.include_router(items_menu.router)
# app.include_router(ordenes.router)