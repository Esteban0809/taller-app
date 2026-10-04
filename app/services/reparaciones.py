from datetime import datetime

from app.models.models import ESTADOS_REPARACION
from app.repositories.reparaciones import ReparacionRepository
from app.repositories.usuarios import UsuarioRepository
from app.repositories.vehiculos import VehiculoRepository
from app.services.base import conflicto, guardar, no_encontrado


class ReparacionService:

    def __init__(self, repository: ReparacionRepository):
        self.repository = repository
        self.vehiculos = VehiculoRepository(repository.db)
        self.usuarios = UsuarioRepository(repository.db)

    def listar(
        self,
        taller_id: int,
        estado: str | None,
        vehiculo_id: int | None,
        activas: bool,
        limite: int,
        offset: int,
    ):
        return self.repository.listar(taller_id, estado, vehiculo_id, activas, limite, offset)

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
        guardar(self.repository.db, reparacion)
        return self.obtener(reparacion.id, taller_id)

    def actualizar(self, reparacion_id: int, taller_id: int, datos: dict):
        reparacion = self.obtener(reparacion_id, taller_id)

        if "mecanico_id" in datos:
            self._comprobar_mecanico(datos["mecanico_id"], taller_id)

        # Un presupuesto nuevo necesita que el cliente lo vuelva a aprobar
        if "presupuesto" in datos and float(datos["presupuesto"]) != float(reparacion.presupuesto):
            reparacion.presupuesto_aprobado_at = None

        self.repository.actualizar(reparacion, datos)
        guardar(self.repository.db, reparacion)
        return self.obtener(reparacion.id, taller_id)

    def cambiar_estado(self, reparacion_id: int, taller_id: int, estado: str):
        reparacion = self.obtener(reparacion_id, taller_id)
        reparacion.estado = estado

        if estado == "entregado":
            reparacion.fecha_entrega = datetime.now()
            if reparacion.precio_final is None:
                reparacion.precio_final = reparacion.presupuesto
        else:
            reparacion.fecha_entrega = None

        guardar(self.repository.db, reparacion)
        return self.obtener(reparacion.id, taller_id)

    def eliminar(self, reparacion_id: int, taller_id: int):
        reparacion = self.obtener(reparacion_id, taller_id)
        self.repository.eliminar(reparacion)
        guardar(self.repository.db)

    def seguimiento(self, token: str):
        reparacion = self.repository.obtener_por_token(token)

        if not reparacion:
            raise no_encontrado("Enlace de seguimiento no válido")

        vehiculo = reparacion.vehiculo
        return {
            "taller_nombre": reparacion.taller.nombre,
            "taller_telefono": reparacion.taller.telefono,
            "cliente_nombre": vehiculo.cliente.nombre.split()[0],
            "matricula": vehiculo.matricula,
            "vehiculo": " ".join(filter(None, [vehiculo.marca, vehiculo.modelo])),
            "descripcion": reparacion.descripcion,
            "estado": reparacion.estado,
            "presupuesto": float(reparacion.presupuesto),
            "presupuesto_aprobado_at": reparacion.presupuesto_aprobado_at,
            "fecha_entrada": reparacion.fecha_entrada,
            "fecha_entrega": reparacion.fecha_entrega,
        }

    def aprobar_presupuesto(self, token: str):
        reparacion = self.repository.obtener_por_token(token)

        if not reparacion:
            raise no_encontrado("Enlace de seguimiento no válido")
        if reparacion.presupuesto <= 0:
            raise conflicto("Todavía no hay presupuesto que aprobar")
        if reparacion.presupuesto_aprobado_at is not None:
            raise conflicto("El presupuesto ya está aprobado")
        if reparacion.estado in ("listo", "entregado"):
            raise conflicto("La reparación ya está terminada")

        reparacion.presupuesto_aprobado_at = datetime.now()
        guardar(self.repository.db, reparacion)
        return self.seguimiento(token)

    def resumen(self, taller_id: int):
        conteo = self.repository.contar_por_estado(taller_id)
        por_estado = {estado: conteo.get(estado, 0) for estado in ESTADOS_REPARACION}

        return {
            "por_estado": por_estado,
            "en_taller": sum(total for estado, total in por_estado.items() if estado != "entregado"),
            "facturado": float(self.repository.total_facturado(taller_id)),
        }
