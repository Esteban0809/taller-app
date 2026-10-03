from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalizar_matricula(valor: str) -> str:
    return valor.replace(" ", "").replace("-", "").upper()


class VehiculoCrear(BaseModel):
    cliente_id: int = Field(gt=0)
    matricula: str = Field(min_length=4, max_length=15)
    marca: str | None = Field(default=None, max_length=50)
    modelo: str | None = Field(default=None, max_length=50)
    anio: int | None = Field(default=None, ge=1900, le=2100)
    kilometros: int | None = Field(default=None, ge=0)

    @field_validator("matricula")
    @classmethod
    def limpiar_matricula(cls, valor: str) -> str:
        return normalizar_matricula(valor)


class VehiculoActualizar(BaseModel):
    cliente_id: int | None = Field(default=None, gt=0)
    matricula: str | None = Field(default=None, min_length=4, max_length=15)
    marca: str | None = Field(default=None, max_length=50)
    modelo: str | None = Field(default=None, max_length=50)
    anio: int | None = Field(default=None, ge=1900, le=2100)
    kilometros: int | None = Field(default=None, ge=0)

    @field_validator("matricula")
    @classmethod
    def limpiar_matricula(cls, valor: str | None) -> str | None:
        return normalizar_matricula(valor) if valor else valor


class VehiculoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    matricula: str
    marca: str | None
    modelo: str | None
    anio: int | None
    kilometros: int | None
    created_at: datetime
