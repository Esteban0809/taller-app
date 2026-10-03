from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


PLANES = ("prueba", "basico", "pro")
ROLES = ("propietario", "mecanico")
ESTADOS_REPARACION = (
    "recibido",
    "diagnostico",
    "esperando_piezas",
    "en_reparacion",
    "listo",
    "entregado",
)


class Taller(Base):
    __tablename__ = "talleres"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    cif: Mapped[str | None] = mapped_column(String(20), unique=True)
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    direccion: Mapped[str | None] = mapped_column(String(255))
    plan: Mapped[str] = mapped_column(
        Enum(*PLANES, name="plan_taller"),
        default="prueba",
        nullable=False,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="taller",
        cascade="all, delete-orphan",
    )


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        ForeignKey("talleres.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(
        Enum(*ROLES, name="rol_usuario"),
        default="mecanico",
        nullable=False,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    taller: Mapped["Taller"] = relationship(back_populates="usuarios")

    @property
    def taller_nombre(self) -> str:
        return self.taller.nombre


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        ForeignKey("talleres.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    notas: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    vehiculos: Mapped[list["Vehiculo"]] = relationship(back_populates="cliente")


class Vehiculo(Base):
    __tablename__ = "vehiculos"
    __table_args__ = (
        UniqueConstraint(
            "taller_id",
            "matricula",
            name="uq_vehiculo_taller_matricula",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        ForeignKey("talleres.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    matricula: Mapped[str] = mapped_column(String(15), nullable=False)
    marca: Mapped[str | None] = mapped_column(String(50))
    modelo: Mapped[str | None] = mapped_column(String(50))
    anio: Mapped[int | None] = mapped_column(SmallInteger)
    kilometros: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    cliente: Mapped["Cliente"] = relationship(back_populates="vehiculos")
    reparaciones: Mapped[list["Reparacion"]] = relationship(
        back_populates="vehiculo",
    )


class Reparacion(Base):
    __tablename__ = "reparaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    taller_id: Mapped[int] = mapped_column(
        ForeignKey("talleres.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey("vehiculos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    mecanico_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        index=True,
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(
        Enum(*ESTADOS_REPARACION, name="estado_reparacion"),
        default="recibido",
        nullable=False,
        index=True,
    )
    presupuesto: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
    )
    precio_final: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    kilometros_entrada: Mapped[int | None]
    fecha_entrada: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="reparaciones")
