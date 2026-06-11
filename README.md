# API Plataforma de Comida

Proyecto desarrollado con FastAPI y PostgreSQL para la gestión de usuarios, restaurantes, ítems de menú y órdenes.

## Implementado

- Configuración de FastAPI y PostgreSQL.
- Modelos con SQLAlchemy:
  - Usuario
  - Restaurante
  - ItemMenu
  - Orden
  - ItemOrden
- Relaciones entre tablas mediante claves foráneas.
- Schemas con Pydantic para validación de datos.
- CRUD básico para:
  - Usuarios
  - Restaurantes
  - Ítems del menú
  - Órdenes
- Autenticación mediante JWT.
- Hash de contraseñas utilizando Argon2 (`pwdlib`).
- Organización del proyecto mediante routers.
- Documentación automática con Swagger (`/docs`).

## Tecnologías utilizadas

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- PyJWT
- pwdlib[argon2]

## Ejecución

```bash
uvicorn main:app --reload