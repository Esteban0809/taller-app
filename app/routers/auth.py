from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import solo_propietario, usuario_actual
from app.database.session import obtener_sesion
from app.repositories.usuarios import UsuarioRepository
from app.schemas.auth import (
    Login,
    RegistroTaller,
    TokenRespuesta,
    UsuarioCrear,
    UsuarioRespuesta,
)
from app.services.auth import AuthService


router = APIRouter(tags=["Auth y usuarios"])


def obtener_servicio(db: Session = Depends(obtener_sesion)):
    return AuthService(UsuarioRepository(db))


@router.post(
    "/auth/registro",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenRespuesta,
)
def registro(
    datos: RegistroTaller,
    service: AuthService = Depends(obtener_servicio),
):
    token = service.registrar_taller(
        datos.taller_nombre,
        datos.nombre,
        datos.email,
        datos.password,
    )
    return {"access_token": token}


@router.post("/auth/login", response_model=TokenRespuesta)
def login(
    datos: Login,
    service: AuthService = Depends(obtener_servicio),
):
    return {"access_token": service.login(datos.email, datos.password)}


@router.get("/auth/me", response_model=UsuarioRespuesta)
def yo(
    usuario=Depends(usuario_actual),
    service: AuthService = Depends(obtener_servicio),
):
    return service.obtener_usuario(usuario["id"], usuario["taller_id"])


@router.get("/usuarios", response_model=list[UsuarioRespuesta])
def listar_usuarios(
    usuario=Depends(solo_propietario),
    service: AuthService = Depends(obtener_servicio),
):
    return service.listar_usuarios(usuario["taller_id"])


@router.post(
    "/usuarios",
    status_code=status.HTTP_201_CREATED,
    response_model=UsuarioRespuesta,
)
def crear_usuario(
    datos: UsuarioCrear,
    usuario=Depends(solo_propietario),
    service: AuthService = Depends(obtener_servicio),
):
    return service.crear_usuario(
        usuario["taller_id"],
        datos.nombre,
        datos.email,
        datos.password,
        datos.rol,
    )
