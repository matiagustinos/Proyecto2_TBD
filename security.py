# auth.py

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import get_db


SECRET_KEY = "clave_secreta_tarea2_tbd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hashear_password(password: str) -> str:
    return password_hash.hash(password)


def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    return password_hash.verify(password_plano, password_hasheado)


def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    datos_a_codificar = data.copy()

    if expires_delta:
        expira = datetime.now(timezone.utc) + expires_delta
    else:
        expira = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    datos_a_codificar.update({"exp": expira})

    token = jwt.encode(
        datos_a_codificar,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def obtener_usuario_por_nombre_usuario(
    db: Session,
    nombre_usuario: str
):
    usuario = db.execute(
        select(models.Usuario).where(
            models.Usuario.nombre_usuario == nombre_usuario
        )
    ).scalar_one_or_none()

    return usuario


def autenticar_usuario(
    db: Session,
    nombre_usuario: str,
    password: str
):
    usuario = obtener_usuario_por_nombre_usuario(db, nombre_usuario)

    if not usuario:
        return None

    if not verificar_password(password, usuario.contrasena_hash):
        return None

    return usuario


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        usuario_id = payload.get("sub")

        if usuario_id is None:
            raise credenciales_exception

    except InvalidTokenError:
        raise credenciales_exception

    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise credenciales_exception

    return usuario


def exigir_rol(*roles_permitidos):
    def validador(
        usuario_actual: models.Usuario = Depends(obtener_usuario_actual)
    ):
        if usuario_actual.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )

        return usuario_actual

    return validador