from tests.conftest import registrar
from tests.test_taller import crear_cliente_y_vehiculo


def crear_reparacion(client, auth, presupuesto=0):
    _, vehiculo = crear_cliente_y_vehiculo(client, auth)
    respuesta = client.post("/reparaciones", headers=auth, json={
        "vehiculo_id": vehiculo["id"],
        "descripcion": "Cambio de pastillas de freno",
        "presupuesto": presupuesto,
    })
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_cada_reparacion_tiene_su_enlace(client, auth):
    a = crear_reparacion(client, auth)
    b = client.post("/reparaciones", headers=auth, json={
        "vehiculo_id": a["vehiculo_id"],
        "descripcion": "Revisión",
    }).json()

    assert len(a["token_seguimiento"]) >= 20
    assert a["token_seguimiento"] != b["token_seguimiento"]


def test_cliente_ve_su_reparacion_sin_login(client, auth):
    reparacion = crear_reparacion(client, auth, presupuesto=120)

    r = client.get(f"/seguimiento/{reparacion['token_seguimiento']}")
    assert r.status_code == 200
    datos = r.json()
    assert datos["taller_nombre"] == "Taller Morrazo"
    assert datos["cliente_nombre"] == "Juan"
    assert datos["matricula"] == "1234ABC"
    assert datos["vehiculo"] == "Seat Ibiza"
    assert datos["estado"] == "recibido"
    assert datos["presupuesto"] == 120


def test_seguimiento_no_expone_datos_internos(client, auth):
    reparacion = crear_reparacion(client, auth)

    datos = client.get(f"/seguimiento/{reparacion['token_seguimiento']}").json()
    for campo in ("id", "taller_id", "vehiculo_id", "mecanico_id", "telefono", "token_seguimiento"):
        assert campo not in datos


def test_token_invalido_da_404(client):
    assert client.get("/seguimiento/no-existe").status_code == 404
    assert client.post("/seguimiento/no-existe/aprobar").status_code == 404


def test_cliente_aprueba_presupuesto_una_sola_vez(client, auth):
    reparacion = crear_reparacion(client, auth, presupuesto=245.50)
    token = reparacion["token_seguimiento"]

    aprobado = client.post(f"/seguimiento/{token}/aprobar")
    assert aprobado.status_code == 200
    assert aprobado.json()["presupuesto_aprobado_at"] is not None

    taller = client.get(f"/reparaciones/{reparacion['id']}", headers=auth).json()
    assert taller["presupuesto_aprobado_at"] is not None

    assert client.post(f"/seguimiento/{token}/aprobar").status_code == 409


def test_no_se_aprueba_sin_presupuesto(client, auth):
    reparacion = crear_reparacion(client, auth, presupuesto=0)
    r = client.post(f"/seguimiento/{reparacion['token_seguimiento']}/aprobar")
    assert r.status_code == 409


def test_no_se_aprueba_reparacion_terminada(client, auth):
    reparacion = crear_reparacion(client, auth, presupuesto=80)
    client.patch(f"/reparaciones/{reparacion['id']}/estado", headers=auth, json={"estado": "listo"})

    r = client.post(f"/seguimiento/{reparacion['token_seguimiento']}/aprobar")
    assert r.status_code == 409


def test_cambiar_presupuesto_anula_la_aprobacion(client, auth):
    reparacion = crear_reparacion(client, auth, presupuesto=100)
    token = reparacion["token_seguimiento"]
    client.post(f"/seguimiento/{token}/aprobar")

    # Guardar el mismo importe no obliga a aprobar de nuevo
    mismo = client.patch(f"/reparaciones/{reparacion['id']}", headers=auth, json={"presupuesto": 100})
    assert mismo.json()["presupuesto_aprobado_at"] is not None

    nuevo = client.patch(f"/reparaciones/{reparacion['id']}", headers=auth, json={"presupuesto": 180})
    assert nuevo.json()["presupuesto_aprobado_at"] is None
    assert client.post(f"/seguimiento/{token}/aprobar").status_code == 200


def test_enlace_de_otro_taller_no_da_acceso_a_su_api(client, auth):
    reparacion = crear_reparacion(client, auth)
    otro = registrar(client, email="otro@taller.com", taller="Otro Taller")

    # El token sirve para la página pública, no para la API privada de otro taller
    assert client.get(f"/reparaciones/{reparacion['id']}", headers=otro).status_code == 404
