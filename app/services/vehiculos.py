from app.repositories.clientes import ClienteRepository
from app.repositories.vehiculos import VehiculoRepository
from app.services.base import conflicto, guardar, no_encontrado


class VehiculoService:

    def __init__(self, repository: VehiculoRepository):
        self.repository = repository
        self.clientes = ClienteRepository(repository.db)

    def listar(self, taller_id: int, cliente_id: int | None, matricula: str | None):
        return self.repository.listar(taller_id, cliente_id, matricula)

    def obtener(self, vehiculo_id: int, taller_id: int):
        vehiculo = self.repository.obtener(vehiculo_id, taller_id)

        if not vehiculo:
            raise no_encontrado("Vehículo no encontrado")

        return vehiculo

    def _comprobar_cliente(self, cliente_id: int, taller_id: int):
        if not self.clientes.obtener(cliente_id, taller_id):
            raise no_encontrado("Cliente no encontrado")

    def _comprobar_matricula_libre(self, matricula: str, taller_id: int):
        if self.repository.obtener_por_matricula(matricula, taller_id):
            raise conflicto(f"Ya existe un vehículo con matrícula {matricula}")

    def crear(self, taller_id: int, datos: dict):
        self._comprobar_cliente(datos["cliente_id"], taller_id)
        self._comprobar_matricula_libre(datos["matricula"], taller_id)

        vehiculo = self.repository.crear(taller_id, datos)
        return guardar(self.repository.db, vehiculo)

    def actualizar(self, vehiculo_id: int, taller_id: int, datos: dict):
        vehiculo = self.obtener(vehiculo_id, taller_id)

        if "cliente_id" in datos and datos["cliente_id"] != vehiculo.cliente_id:
            self._comprobar_cliente(datos["cliente_id"], taller_id)

        if "matricula" in datos and datos["matricula"] != vehiculo.matricula:
            self._comprobar_matricula_libre(datos["matricula"], taller_id)

        self.repository.actualizar(vehiculo, datos)
        return guardar(self.repository.db, vehiculo)

    def eliminar(self, vehiculo_id: int, taller_id: int):
        vehiculo = self.obtener(vehiculo_id, taller_id)

        if self.repository.contar_reparaciones(vehiculo.id):
            raise conflicto("El vehículo tiene reparaciones y no se puede eliminar")

        self.repository.eliminar(vehiculo)
        guardar(self.repository.db)
