from datetime import datetime

from app.models.models import ESTADOS_REPARACION
from app.repositories.reparaciones import ReparacionRepository
from app.repositories.usuarios import UsuarioRepository
from app.repositories.vehiculos import VehiculoRepository
from app.services.base import guardar, no_encontrado


class ReparacionService:

    def __init__(self, repository: ReparacionRepository):
        self.repository = repository
        self.vehiculos = VehiculoRepository(repository.db)
        self.usuarios = UsuarioRepository(repository.db)

    def listar(self, taller_id: int, estado: str | None, vehiculo_id: int | None, limite: int, offset: int):
        return self.repository.listar(taller_id, estado, vehiculo_id, limite, offset)

    def obtener(self, reparacion_id: int, taller_id: int):
        reparacion = self.repository.obtener(reparacion_id, taller_id)

        if not reparacion:
            raise no_encontrado("Reparación no encontrada")

        return reparacion

    def _comprobar_mecanico(self, mecanico_id: int | None, taller_id: int):
        if mecanico_id and not self.usuarios.obtener(mecanico_id, taller_id):
            raise no_encontrado("Mecánico no encontrado")

    def crear(self, taller_id: int, datos: dict):
        vehiculo = self.vehiculos.obtener(datos["vehiculo_id"], taller_id)

        if not vehiculo:
            raise no_encontrado("Vehículo no encontrado")

        self._comprobar_mecanico(datos.get("mecanico_id"), taller_id)

        kilometros = datos.get("kilometros_entrada")
        if kilometros and kilometros > (vehiculo.kilometros or 0):
            vehiculo.kilometros = kilometros

        reparacion = self.repository.crear(taller_id, datos)
        return guardar(self.repository.db, reparacion)

    def actualizar(self, reparacion_id: int, taller_id: int, datos: dict):
        reparacion = self.obtener(reparacion_id, taller_id)

        if "mecanico_id" in datos:
            self._comprobar_mecanico(datos["mecanico_id"], taller_id)

        self.repository.actualizar(reparacion, datos)
        return guardar(self.repository.db, reparacion)

    def cambiar_estado(self, reparacion_id: int, taller_id: int, estado: str):
        reparacion = self.obtener(reparacion_id, taller_id)
        reparacion.estado = estado

        if estado == "entregado":
            reparacion.fecha_entrega = datetime.now()
            if reparacion.precio_final is None:
                reparacion.precio_final = reparacion.presupuesto
        else:
            reparacion.fecha_entrega = None

        return guardar(self.repository.db, reparacion)

    def eliminar(self, reparacion_id: int, taller_id: int):
        reparacion = self.obtener(reparacion_id, taller_id)
        self.repository.eliminar(reparacion)
        guardar(self.repository.db)

    def resumen(self, taller_id: int):
        conteo = self.repository.contar_por_estado(taller_id)
        por_estado = {estado: conteo.get(estado, 0) for estado in ESTADOS_REPARACION}

        return {
            "por_estado": por_estado,
            "en_taller": sum(total for estado, total in por_estado.items() if estado != "entregado"),
            "facturado": float(self.repository.total_facturado(taller_id)),
        }
