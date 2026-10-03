from tests.conftest import registrar


def crear_cliente_y_vehiculo(client, auth):
    cliente = client.post("/clientes", headers=auth, json={
        "nombre": "Juan Pérez",
        "telefono": "600111222",
    }).json()

    vehiculo = client.post("/vehiculos", headers=auth, json={
        "cliente_id": cliente["id"],
        "matricula": "1234 abc",
        "marca": "Seat",
        "modelo": "Ibiza",
        "kilometros": 145000,
    })
    assert vehiculo.status_code == 201, vehiculo.text

    return cliente, vehiculo.json()


def test_matricula_se_normaliza_y_no_se_repite(client, auth):
    cliente, vehiculo = crear_cliente_y_vehiculo(client, auth)

    assert vehiculo["matricula"] == "1234ABC"

    repetido = client.post("/vehiculos", headers=auth, json={
        "cliente_id": cliente["id"],
        "matricula": "1234-ABC",
    })
    assert repetido.status_code == 409


def test_flujo_completo_de_una_reparacion(client, auth):
    _, vehiculo = crear_cliente_y_vehiculo(client, auth)

    creada = client.post("/reparaciones", headers=auth, json={
        "vehiculo_id": vehiculo["id"],
        "descripcion": "Cambio de aceite y filtros",
        "presupuesto": 89.90,
        "kilometros_entrada": 146000,
    })
    assert creada.status_code == 201, creada.text
    reparacion = creada.json()
    assert reparacion["estado"] == "recibido"

    km = client.get(f"/vehiculos/{vehiculo['id']}", headers=auth).json()["kilometros"]
    assert km == 146000

    for estado in ("diagnostico", "en_reparacion", "listo"):
        r = client.patch(f"/reparaciones/{reparacion['id']}/estado", headers=auth, json={"estado": estado})
        assert r.status_code == 200
        assert r.json()["fecha_entrega"] is None

    entregada = client.patch(
        f"/reparaciones/{reparacion['id']}/estado",
        headers=auth,
        json={"estado": "entregado"},
    ).json()
    assert entregada["fecha_entrega"] is not None
    assert entregada["precio_final"] == 89.90

    resumen = client.get("/reparaciones/resumen", headers=auth).json()
    assert resumen["por_estado"]["entregado"] == 1
    assert resumen["en_taller"] == 0
    assert resumen["facturado"] == 89.90


def test_estado_invalido_da_422(client, auth):
    _, vehiculo = crear_cliente_y_vehiculo(client, auth)
    reparacion = client.post("/reparaciones", headers=auth, json={
        "vehiculo_id": vehiculo["id"],
        "descripcion": "Frenos",
    }).json()

    r = client.patch(f"/reparaciones/{reparacion['id']}/estado", headers=auth, json={"estado": "volando"})
    assert r.status_code == 422


def test_no_se_borra_cliente_con_vehiculos(client, auth):
    cliente, _ = crear_cliente_y_vehiculo(client, auth)

    respuesta = client.delete(f"/clientes/{cliente['id']}", headers=auth)
    assert respuesta.status_code == 409


def test_un_taller_no_ve_los_datos_de_otro(client, auth):
    cliente, vehiculo = crear_cliente_y_vehiculo(client, auth)
    otro = registrar(client, email="otro@tallervigo.com", taller="Taller Vigo")

    assert client.get("/clientes", headers=otro).json() == []
    assert client.get(f"/clientes/{cliente['id']}", headers=otro).status_code == 404
    assert client.get(f"/vehiculos/{vehiculo['id']}", headers=otro).status_code == 404

    robo = client.post("/vehiculos", headers=otro, json={
        "cliente_id": cliente["id"],
        "matricula": "9999ZZZ",
    })
    assert robo.status_code == 404

    reparacion = client.post("/reparaciones", headers=otro, json={
        "vehiculo_id": vehiculo["id"],
        "descripcion": "Intento de colarse",
    })
    assert reparacion.status_code == 404
