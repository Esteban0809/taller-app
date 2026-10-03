import os
import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from dotenv import load_dotenv

load_dotenv()

password_hash = PasswordHash.recommended()
SECRET = os.getenv("JWT_SECRET")

if not SECRET or len(SECRET.encode()) < 32:
    raise RuntimeError("JWT_SECRET debe tener al menos 32 bytes")

ALGORITHM = "HS256"


def crear_hash(password: str) -> str:
    return password_hash.hash(password)


def verificar_password(password: str, hash_guardado: str) -> bool:
    return password_hash.verify(password, hash_guardado)


def crear_token(usuario_id: int, email: str, taller_id: int, rol: str) -> str:
    payload = {
        "sub": email,
        "user_id": usuario_id,
        "taller_id": taller_id,
        "rol": rol,
        "exp": datetime.now(timezone.utc) + timedelta(hours=8)
    }

    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def verificar_token(token: str):
    return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
