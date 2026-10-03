from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EstadoReparacion = Literal[
    "recibido",
    "diagnostico",
    "esperando_piezas",
    "en_reparacion",
    "listo",
    "entregado",
]


class ReparacionCrear(BaseModel):
    vehiculo_id: int = Field(gt=0)
    descripcion: str = Field(min_length=3)
    mecanico_id: int | None = Field(default=None, gt=0)
    presupuesto: float = Field(default=0, ge=0)
    kilometros_entrada: int | None = Field(default=None, ge=0)


class ReparacionActualizar(BaseModel):
    descripcion: str | None = Field(default=None, min_length=3)
    mecanico_id: int | None = Field(default=None, gt=0)
    presupuesto: float | None = Field(default=None, ge=0)
    precio_final: float | None = Field(default=None, ge=0)
    kilometros_entrada: int | None = Field(default=None, ge=0)


class CambioEstado(BaseModel):
    estado: EstadoReparacion


class ReparacionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehiculo_id: int
    mecanico_id: int | None
    descripcion: str
    estado: str
    presupuesto: float
    precio_final: float | None
    kilometros_entrada: int | None
    fecha_entrada: datetime
    fecha_entrega: datetime | None


class ResumenTaller(BaseModel):
    por_estado: dict[str, int]
    en_taller: int
    facturado: float
