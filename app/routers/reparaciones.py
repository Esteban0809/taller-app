from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import solo_propietario, usuario_actual
from app.database.session import obtener_sesion
from app.repositories.reparaciones import ReparacionRepository
from app.schemas.reparaciones import (
    CambioEstado,
    EstadoReparacion,
    ReparacionActualizar,
    ReparacionCrear,
    ReparacionRespuesta,
    ResumenTaller,
)
from app.services.reparaciones import ReparacionService


router = APIRouter(prefix="/reparaciones", tags=["Reparaciones"])


def obtener_servicio(db: Session = Depends(obtener_sesion)):
    return ReparacionService(ReparacionRepository(db))


@router.get("", response_model=list[ReparacionRespuesta])
def listar(
    estado: EstadoReparacion | None = None,
    vehiculo_id: int | None = None,
    activas: bool = False,
    limite: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    usuario=Depends(usuario_actual),
    service: ReparacionService = Depends(obtener_servicio),
):
    return service.listar(usuario["taller_id"], estado, vehiculo_id, activas, limite, offset)


@router.get("/resumen", response_model=ResumenTaller)
def resumen(
    usuario=Depends(usuario_actual),
    service: ReparacionService = Depends(obtener_servicio),
):
    return service.resumen(usuario["taller_id"])


@router.get("/{reparacion_id}", response_model=ReparacionRespuesta)
def obtener(
    reparacion_id: int,
    usuario=Depends(usuario_actual),
    service: ReparacionService = Depends(obtener_servicio),
):
    return service.obtener(reparacion_id, usuario["taller_id"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReparacionRespuesta)
def crear(
    datos: ReparacionCrear,
    usuario=Depends(usuario_actual),
    service: ReparacionService = Depends(obtener_servicio),
):
    return service.crear(usuario["taller_id"], datos.model_dump())


@router.patch("/{reparacion_id}", response_model=ReparacionRespuesta)
def actualizar(
    reparacion_id: int,
    datos: ReparacionActualizar,
    usuario=Depends(usuario_actual),
    service: ReparacionService = Depends(obtener_servicio),
):
    return service.actualizar(
        reparacion_id,
        usuario["taller_id"],
        datos.model_dump(exclude_unset=True),
    )


@router.patch("/{reparacion_id}/estado", response_model=ReparacionRespuesta)
def cambiar_estado(
    reparacion_id: int,
    datos: CambioEstado,
    usuario=Depends(usuario_actual),
    service: ReparacionService = Depends(obtener_servicio),
):
    return service.cambiar_estado(reparacion_id, usuario["taller_id"], datos.estado)


@router.delete("/{reparacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    reparacion_id: int,
    usuario=Depends(solo_propietario),
    service: ReparacionService = Depends(obtener_servicio),
):
    service.eliminar(reparacion_id, usuario["taller_id"])
