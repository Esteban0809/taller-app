from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import usuario_actual
from app.database.session import obtener_sesion
from app.repositories.clientes import ClienteRepository
from app.schemas.clientes import ClienteActualizar, ClienteCrear, ClienteRespuesta
from app.services.clientes import ClienteService


router = APIRouter(prefix="/clientes", tags=["Clientes"])


def obtener_servicio(db: Session = Depends(obtener_sesion)):
    return ClienteService(ClienteRepository(db))


@router.get("", response_model=list[ClienteRespuesta])
def listar(
    buscar: str | None = None,
    limite: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    usuario=Depends(usuario_actual),
    service: ClienteService = Depends(obtener_servicio),
):
    return service.listar(usuario["taller_id"], buscar, limite, offset)


@router.get("/{cliente_id}", response_model=ClienteRespuesta)
def obtener(
    cliente_id: int,
    usuario=Depends(usuario_actual),
    service: ClienteService = Depends(obtener_servicio),
):
    return service.obtener(cliente_id, usuario["taller_id"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ClienteRespuesta)
def crear(
    datos: ClienteCrear,
    usuario=Depends(usuario_actual),
    service: ClienteService = Depends(obtener_servicio),
):
    return service.crear(usuario["taller_id"], datos.model_dump())


@router.patch("/{cliente_id}", response_model=ClienteRespuesta)
def actualizar(
    cliente_id: int,
    datos: ClienteActualizar,
    usuario=Depends(usuario_actual),
    service: ClienteService = Depends(obtener_servicio),
):
    return service.actualizar(
        cliente_id,
        usuario["taller_id"],
        datos.model_dump(exclude_unset=True),
    )


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    cliente_id: int,
    usuario=Depends(usuario_actual),
    service: ClienteService = Depends(obtener_servicio),
):
    service.eliminar(cliente_id, usuario["taller_id"])
