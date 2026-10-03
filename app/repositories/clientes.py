from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.models import Cliente, Vehiculo


class ClienteRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar(self, taller_id: int, buscar: str | None, limite: int, offset: int):
        consulta = select(Cliente).where(Cliente.taller_id == taller_id)

        if buscar:
            patron = f"%{buscar}%"
            consulta = consulta.where(
                or_(
                    Cliente.nombre.ilike(patron),
                    Cliente.telefono.ilike(patron),
                    Cliente.email.ilike(patron),
                )
            )

        consulta = consulta.order_by(Cliente.nombre).limit(limite).offset(offset)
        return list(self.db.scalars(consulta))

    def obtener(self, cliente_id: int, taller_id: int):
        return self.db.scalar(
            select(Cliente).where(
                Cliente.id == cliente_id,
                Cliente.taller_id == taller_id,
            )
        )

    def crear(self, taller_id: int, datos: dict):
        cliente = Cliente(taller_id=taller_id, **datos)
        self.db.add(cliente)
        self.db.flush()
        return cliente

    def actualizar(self, cliente: Cliente, datos: dict):
        for campo, valor in datos.items():
            setattr(cliente, campo, valor)
        self.db.flush()
        return cliente

    def contar_vehiculos(self, cliente_id: int):
        return self.db.scalar(
            select(func.count(Vehiculo.id)).where(Vehiculo.cliente_id == cliente_id)
        )

    def eliminar(self, cliente: Cliente):
        self.db.delete(cliente)
        self.db.flush()
