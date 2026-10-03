from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import usuario_actual
from app.database.session import obtener_sesion
from app.repositories.vehiculos import VehiculoRepository
from app.schemas.vehiculos import VehiculoActualizar, VehiculoCrear, VehiculoRespuesta
from app.services.vehiculos import VehiculoService


router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


def obtener_servicio(db: Session = Depends(obtener_sesion)):
    return VehiculoService(VehiculoRepository(db))


@router.get("", response_model=list[VehiculoRespuesta])
def listar(
    cliente_id: int | None = None,
    matricula: str | None = None,
    usuario=Depends(usuario_actual),
    service: VehiculoService = Depends(obtener_servicio),
):
    return service.listar(usuario["taller_id"], cliente_id, matricula)


@router.get("/{vehiculo_id}", response_model=VehiculoRespuesta)
def obtener(
    vehiculo_id: int,
    usuario=Depends(usuario_actual),
    service: VehiculoService = Depends(obtener_servicio),
):
    return service.obtener(vehiculo_id, usuario["taller_id"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=VehiculoRespuesta)
def crear(
    datos: VehiculoCrear,
    usuario=Depends(usuario_actual),
    service: VehiculoService = Depends(obtener_servicio),
):
    return service.crear(usuario["taller_id"], datos.model_dump())


@router.patch("/{vehiculo_id}", response_model=VehiculoRespuesta)
def actualizar(
    vehiculo_id: int,
    datos: VehiculoActualizar,
    usuario=Depends(usuario_actual),
    service: VehiculoService = Depends(obtener_servicio),
):
    return service.actualizar(
        vehiculo_id,
        usuario["taller_id"],
        datos.model_dump(exclude_unset=True),
    )


@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    vehiculo_id: int,
    usuario=Depends(usuario_actual),
    service: VehiculoService = Depends(obtener_servicio),
):
    service.eliminar(vehiculo_id, usuario["taller_id"])
