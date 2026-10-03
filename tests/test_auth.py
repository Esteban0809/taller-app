from tests.conftest import registrar


def test_registro_crea_taller_y_propietario(client, auth):
    respuesta = client.get("/auth/me", headers=auth)

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "propietario"
    assert respuesta.json()["email"] == "dueno@tallermorrazo.com"


def test_registro_con_email_repetido_da_409(client, auth):
    respuesta = client.post("/auth/registro", json={
        "taller_nombre": "Otro",
        "nombre": "Otro",
        "email": "dueno@tallermorrazo.com",
        "password": "contraseña-segura",
    })

    assert respuesta.status_code == 409


def test_login(client, auth):
    ok = client.post("/auth/login", json={
        "email": "dueno@tallermorrazo.com",
        "password": "contraseña-segura",
    })
    mal = client.post("/auth/login", json={
        "email": "dueno@tallermorrazo.com",
        "password": "incorrecta",
    })

    assert ok.status_code == 200
    assert "access_token" in ok.json()
    assert mal.status_code == 401


def test_endpoints_protegidos_sin_token(client):
    for url in ("/clientes", "/vehiculos", "/reparaciones", "/auth/me"):
        assert client.get(url).status_code in (401, 403)


def test_mecanico_no_puede_crear_usuarios(client, auth):
    creado = client.post("/usuarios", headers=auth, json={
        "nombre": "Manolo",
        "email": "manolo@tallermorrazo.com",
        "password": "contraseña-segura",
    })
    assert creado.status_code == 201
    assert creado.json()["rol"] == "mecanico"

    login = client.post("/auth/login", json={
        "email": "manolo@tallermorrazo.com",
        "password": "contraseña-segura",
    })
    mecanico = {"Authorization": f"Bearer {login.json()['access_token']}"}

    respuesta = client.post("/usuarios", headers=mecanico, json={
        "nombre": "Intruso",
        "email": "intruso@tallermorrazo.com",
        "password": "contraseña-segura",
    })
    assert respuesta.status_code == 403
