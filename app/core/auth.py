from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.core.security import verificar_token

security = HTTPBearer()


def usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = verificar_token(credentials.credentials)

        usuario_id = payload.get("user_id")
        email = payload.get("sub")
        taller_id = payload.get("taller_id")
        rol = payload.get("rol")

        if not usuario_id or not email or not taller_id or not rol:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        return {
            "id": usuario_id,
            "email": email,
            "taller_id": taller_id,
            "rol": rol
        }

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o caducado"
        )


def solo_propietario(usuario=Depends(usuario_actual)):
    if usuario["rol"] != "propietario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el propietario del taller puede hacer esto"
        )

    return usuario
