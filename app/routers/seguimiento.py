from fastapi import APIRouter, Depends

from app.routers.reparaciones import obtener_servicio
from app.schemas.reparaciones import Seguimiento
from app.services.reparaciones import ReparacionService


# Rutas públicas: el token del enlace es la única credencial del cliente
router = APIRouter(prefix="/seguimiento", tags=["Seguimiento (público)"])


@router.get("/{token}", response_model=Seguimiento)
def ver(token: str, service: ReparacionService = Depends(obtener_servicio)):
    return service.seguimiento(token)


@router.post("/{token}/aprobar", response_model=Seguimiento)
def aprobar_presupuesto(token: str, service: ReparacionService = Depends(obtener_servicio)):
    return service.aprobar_presupuesto(token)
