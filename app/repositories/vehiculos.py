from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import Reparacion, Vehiculo


class VehiculoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self, taller_id: int, cliente_id: int | None, matricula: str | None):
        consulta = select(Vehiculo).where(Vehiculo.taller_id == taller_id)

        if cliente_id:
            consulta = consulta.where(Vehiculo.cliente_id == cliente_id)

        if matricula:
            consulta = consulta.where(Vehiculo.matricula.ilike(f"%{matricula}%"))

        return list(self.db.scalars(consulta.order_by(Vehiculo.matricula)))

    def obtener(self, vehiculo_id: int, taller_id: int):
        return self.db.scalar(
            select(Vehiculo).where(
                Vehiculo.id == vehiculo_id,
                Vehiculo.taller_id == taller_id,
            )
        )

    def obtener_por_matricula(self, matricula: str, taller_id: int):
        return self.db.scalar(
            select(Vehiculo).where(
                Vehiculo.matricula == matricula,
                Vehiculo.taller_id == taller_id,
            )
        )

    def crear(self, taller_id: int, datos: dict):
        vehiculo = Vehiculo(taller_id=taller_id, **datos)
        self.db.add(vehiculo)
        self.db.flush()
        return vehiculo

    def actualizar(self, vehiculo: Vehiculo, datos: dict):
        for campo, valor in datos.items():
            setattr(vehiculo, campo, valor)
        self.db.flush()
        return vehiculo

    def contar_reparaciones(self, vehiculo_id: int):
        return self.db.scalar(
            select(func.count(Reparacion.id)).where(Reparacion.vehiculo_id == vehiculo_id)
        )

    def eliminar(self, vehiculo: Vehiculo):
        self.db.delete(vehiculo)
        self.db.flush()
