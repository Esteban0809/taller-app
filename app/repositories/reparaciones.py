from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.models import Reparacion, Vehiculo


CON_VEHICULO = selectinload(Reparacion.vehiculo).selectinload(Vehiculo.cliente)


class ReparacionRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(
        self,
        taller_id: int,
        estado: str | None,
        vehiculo_id: int | None,
        activas: bool,
        limite: int,
        offset: int,
    ):
        consulta = (
            select(Reparacion)
            .options(CON_VEHICULO)
            .where(Reparacion.taller_id == taller_id)
        )

        if activas:
            consulta = consulta.where(Reparacion.estado != "entregado")

        if estado:
            consulta = consulta.where(Reparacion.estado == estado)

        if vehiculo_id:
            consulta = consulta.where(Reparacion.vehiculo_id == vehiculo_id)

        consulta = (
            consulta.order_by(Reparacion.fecha_entrada.desc(), Reparacion.id.desc())
            .limit(limite)
            .offset(offset)
        )
        return list(self.db.scalars(consulta))

    def obtener(self, reparacion_id: int, taller_id: int):
        return self.db.scalar(
            select(Reparacion).options(CON_VEHICULO).where(
                Reparacion.id == reparacion_id,
                Reparacion.taller_id == taller_id,
            )
        )

    def crear(self, taller_id: int, datos: dict):
        reparacion = Reparacion(taller_id=taller_id, **datos)
        self.db.add(reparacion)
        self.db.flush()
        return reparacion

    def actualizar(self, reparacion: Reparacion, datos: dict):
        for campo, valor in datos.items():
            setattr(reparacion, campo, valor)
        self.db.flush()
        return reparacion

    def eliminar(self, reparacion: Reparacion):
        self.db.delete(reparacion)
        self.db.flush()

    def contar_por_estado(self, taller_id: int):
        filas = self.db.execute(
            select(Reparacion.estado, func.count(Reparacion.id))
            .where(Reparacion.taller_id == taller_id)
            .group_by(Reparacion.estado)
        )
        return {estado: total for estado, total in filas}

    def total_facturado(self, taller_id: int):
        return self.db.scalar(
            select(func.coalesce(func.sum(Reparacion.precio_final), 0))
            .where(
                Reparacion.taller_id == taller_id,
                Reparacion.estado == "entregado",
            )
        )
