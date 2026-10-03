import os

os.environ.setdefault("JWT_SECRET", "test-secret-key-with-more-than-32-bytes-123456789")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import obtener_sesion
from app.main import app
from app.models import models  # noqa: F401  (registra las tablas en Base)


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def activar_foreign_keys(conexion, _):
    conexion.execute("PRAGMA foreign_keys=ON")


SesionTest = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def sesion_test():
    db = SesionTest()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(engine)
    app.dependency_overrides[obtener_sesion] = sesion_test

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def registrar(client, email="dueno@tallermorrazo.com", taller="Taller Morrazo"):
    respuesta = client.post("/auth/registro", json={
        "taller_nombre": taller,
        "nombre": "Esteban",
        "email": email,
        "password": "contraseña-segura",
    })
    assert respuesta.status_code == 201, respuesta.text
    return {"Authorization": f"Bearer {respuesta.json()['access_token']}"}


@pytest.fixture
def auth(client):
    return registrar(client)
