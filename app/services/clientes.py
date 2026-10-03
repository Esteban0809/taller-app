from app.repositories.clientes import ClienteRepository
from app.services.base import conflicto, guardar, no_encontrado


class ClienteService:

    def __init__(self, repository: ClienteRepository):
        self.repository = repository

    def listar(self, taller_id: int, buscar: str | None, limite: int, offset: int):
        return self.repository.listar(taller_id, buscar, limite, offset)

    def obtener(self, cliente_id: int, taller_id: int):
        cliente = self.repository.obtener(cliente_id, taller_id)

        if not cliente:
            raise no_encontrado("Cliente no encontrado")

        return cliente

    def crear(self, taller_id: int, datos: dict):
        cliente = self.repository.crear(taller_id, datos)
        return guardar(self.repository.db, cliente)

    def actualizar(self, cliente_id: int, taller_id: int, datos: dict):
        cliente = self.obtener(cliente_id, taller_id)
        self.repository.actualizar(cliente, datos)
        return guardar(self.repository.db, cliente)

    def eliminar(self, cliente_id: int, taller_id: int):
        cliente = self.obtener(cliente_id, taller_id)

        if self.repository.contar_vehiculos(cliente.id):
            raise conflicto("El cliente tiene vehículos. Elimínalos primero.")

        self.repository.eliminar(cliente)
        guardar(self.repository.db)
