from fastapi import HTTPException, status

from app.core.security import crear_hash, crear_token, verificar_password
from app.repositories.usuarios import UsuarioRepository
from app.services.base import conflicto, guardar


class AuthService:

    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def registrar_taller(self, taller_nombre: str, nombre: str, email: str, password: str):
        if self.repository.obtener_por_email(email):
            raise conflicto("Ya existe un usuario con ese email")

        taller = self.repository.crear_taller(taller_nombre)
        usuario = self.repository.crear(
            taller.id,
            nombre,
            email,
            crear_hash(password),
            "propietario",
        )
        guardar(self.repository.db, usuario)

        return crear_token(usuario.id, usuario.email, usuario.taller_id, usuario.rol)

    def login(self, email: str, password: str):
        usuario = self.repository.obtener_por_email(email)

        if not usuario or not verificar_password(password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )

        if not usuario.activo or not usuario.taller.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada",
            )

        return crear_token(usuario.id, usuario.email, usuario.taller_id, usuario.rol)

    def obtener_usuario(self, usuario_id: int, taller_id: int):
        usuario = self.repository.obtener(usuario_id, taller_id)

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return usuario

    def listar_usuarios(self, taller_id: int):
        return self.repository.listar(taller_id)

    def crear_usuario(self, taller_id: int, nombre: str, email: str, password: str, rol: str):
        if self.repository.obtener_por_email(email):
            raise conflicto("Ya existe un usuario con ese email")

        usuario = self.repository.crear(taller_id, nombre, email, crear_hash(password), rol)
        return guardar(self.repository.db, usuario)
