from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Taller, Usuario


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_por_email(self, email: str):
        return self.db.scalar(
            select(Usuario).where(Usuario.email == email)
        )

    def obtener(self, usuario_id: int, taller_id: int):
        return self.db.scalar(
            select(Usuario).where(
                Usuario.id == usuario_id,
                Usuario.taller_id == taller_id,
            )
        )

    def listar(self, taller_id: int):
        return list(self.db.scalars(
            select(Usuario)
            .where(Usuario.taller_id == taller_id)
            .order_by(Usuario.nombre)
        ))

    def crear_taller(self, nombre: str):
        taller = Taller(nombre=nombre)
        self.db.add(taller)
        self.db.flush()
        return taller

    def crear(self, taller_id: int, nombre: str, email: str, password_hash: str, rol: str):
        usuario = Usuario(
            taller_id=taller_id,
            nombre=nombre,
            email=email,
            password_hash=password_hash,
            rol=rol,
        )
        self.db.add(usuario)
        self.db.flush()
        return usuario
