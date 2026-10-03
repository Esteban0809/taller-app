from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    notas: str | None = None


class ClienteActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    notas: str | None = None


class ClienteRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    telefono: str | None
    email: str | None
    notas: str | None
    created_at: datetime
