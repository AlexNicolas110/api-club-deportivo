def test_obtener_cancha_por_id(client):
    response = client.get("/canchas/2")

    assert response.status_code == 200

    cancha = response.get_json()

    assert cancha["id"] == 2
    assert cancha["nombre"] == "Cancha Test Pádel"
    assert cancha["id_deporte"] == 2
    assert cancha["precio_hora"] == 750000
    assert cancha["techada"] is True
    assert cancha["activa"] is True


def test_obtener_cancha_inexistente_devuelve_404(client):
    response = client.get("/canchas/99999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_NO_ENCONTRADO"
    assert data["errors"][0]["message"] == "Cancha no encontrada"
    assert (
        data["errors"][0]["description"]
        == "No se encontró una cancha con el ID indicado."
    )


def test_crear_cancha_correctamente(client, db):
    nueva_cancha = {
        "nombre": "Cancha Nueva Test",
        "id_deporte": 2,
        "precio_hora": 900000,
        "techada": True,
    }

    response = client.post("/canchas", json=nueva_cancha)

    assert response.status_code == 201
    assert response.data == b""

                                                           
    cur = db.cursor(dictionary=True)
    cur.execute(
        """
        SELECT nombre, id_deporte, precio_hora, techada, activa
        FROM canchas
        WHERE nombre = %s
        """,
        ("Cancha Nueva Test",),
    )
    cancha = cur.fetchone()
    cur.close()

    assert cancha is not None
    assert cancha["nombre"] == "Cancha Nueva Test"
    assert cancha["id_deporte"] == 2
    assert cancha["precio_hora"] == 900000
    assert cancha["techada"] in (1, True)
    assert cancha["activa"] in (1, True)


def test_crear_cancha_con_deporte_inexistente_devuelve_404(client, db):
    nueva_cancha = {
        "nombre": "Cancha Deporte Fantasma",
        "id_deporte": 99999,
        "precio_hora": 900000,
        "techada": False,
    }

    response = client.post("/canchas", json=nueva_cancha)

    assert response.status_code == 404

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_NO_ENCONTRADO"

                                                  
    cur = db.cursor()
    cur.execute(
        """
        SELECT COUNT(*)
        FROM canchas
        WHERE nombre = %s
        """,
        ("Cancha Deporte Fantasma",),
    )
    cantidad = cur.fetchone()[0]
    cur.close()

    assert cantidad == 0


def test_buscar_cancha_por_nombre_es_parcial_e_insensible_a_mayusculas(client):
    response = client.get("/canchas?nombre=pÁdEl")

    assert response.status_code == 200

    data = response.get_json()

    assert "canchas" in data
    assert len(data["canchas"]) == 1

    cancha = data["canchas"][0]

    assert cancha["id"] == 2
    assert cancha["nombre"] == "Cancha Test Pádel"
    assert cancha["id_deporte"] == 2
    assert cancha["precio_hora"] == 750000
    assert cancha["techada"] is True
    assert cancha["activa"] is True


def test_filtrar_canchas_por_deporte(client):
    response = client.get("/canchas?id_deporte=2")

    assert response.status_code == 200

    data = response.get_json()

    assert "canchas" in data
    assert len(data["canchas"]) == 1

    cancha = data["canchas"][0]

    assert cancha["id"] == 2
    assert cancha["nombre"] == "Cancha Test Pádel"
    assert cancha["id_deporte"] == 2
    assert cancha["techada"] is True
    assert cancha["activa"] is True


def test_combinar_filtros_de_canchas_aplica_and(client):
    response = client.get(
        "/canchas?id_deporte=2&techada=true&activa=true"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "canchas" in data
    assert len(data["canchas"]) == 1

    cancha = data["canchas"][0]

    assert cancha["id"] == 2
    assert cancha["nombre"] == "Cancha Test Pádel"
    assert cancha["id_deporte"] == 2
    assert cancha["techada"] is True
    assert cancha["activa"] is True


def test_combinar_filtros_sin_resultados_devuelve_204(client):
    response = client.get(
        "/canchas?id_deporte=2&techada=false"
    )

    assert response.status_code == 204
    assert response.data == b""


def test_filtrar_canchas_rechaza_booleano_invalido(client):
    response = client.get("/canchas?activa=yes")

    assert response.status_code == 400

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_VALIDACION"
    assert data["errors"][0]["message"] == "Filtro inválido"
    assert data["errors"][0]["description"] == "activa debe ser true o false"


def test_modificar_cancha(client):
    response = client.patch(
        "/canchas/2",
        json={
            "nombre": "Cancha Pádel Modificada",
            "precio_hora": 800000,
            "techada": False,
        },
    )

    assert response.status_code == 204
    assert response.data == b""

    response_get = client.get("/canchas/2")

    assert response_get.status_code == 200

    cancha = response_get.get_json()

    assert cancha["id"] == 2
    assert cancha["nombre"] == "Cancha Pádel Modificada"
    assert cancha["id_deporte"] == 2
    assert cancha["precio_hora"] == 800000
    assert cancha["techada"] is False
    assert cancha["activa"] is True


def test_modificar_cancha_inexistente_devuelve_404(client):
    response = client.patch(
        "/canchas/99999",
        json={"nombre": "Cancha Fantasma"},
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_NO_ENCONTRADO"
    assert data["errors"][0]["message"] == "Cancha no encontrada"
    assert (
        data["errors"][0]["description"]
        == "No se encontró una cancha con el ID indicado."
    )


def test_modificar_cancha_rechaza_cuerpo_vacio(client):
    response = client.patch(
        "/canchas/2",
        json={},
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_VALIDACION"
    assert data["errors"][0]["message"] == "Datos de actualización inválidos"
    assert data["errors"][0]["description"] == "Debe indicar al menos un campo para actualizar"

                                       
    response_get = client.get("/canchas/2")

    assert response_get.status_code == 200

    cancha = response_get.get_json()

    assert cancha["id"] == 2
    assert cancha["nombre"] == "Cancha Test Pádel"
    assert cancha["id_deporte"] == 2
    assert cancha["precio_hora"] == 750000
    assert cancha["techada"] is True
    assert cancha["activa"] is True


def test_modificar_cancha_rechaza_campo_desconocido(client):
    response = client.patch(
        "/canchas/2",
        json={"color": "azul"},
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_VALIDACION"
    assert data["errors"][0]["message"] == "Datos de actualización inválidos"
    assert data["errors"][0]["description"] == "Campo(s) desconocido(s): color"

                                       
    response_get = client.get("/canchas/2")

    assert response_get.status_code == 200

    cancha = response_get.get_json()

    assert cancha["id"] == 2
    assert cancha["nombre"] == "Cancha Test Pádel"
    assert cancha["id_deporte"] == 2
    assert cancha["precio_hora"] == 750000
    assert cancha["techada"] is True
    assert cancha["activa"] is True


def test_modificar_estado_activo_de_cancha(client):
    response = client.patch(
        "/canchas/2",
        json={"activa": False},
    )

    assert response.status_code == 204
    assert response.data == b""

    response_get = client.get("/canchas/2")

    assert response_get.status_code == 200

    cancha = response_get.get_json()

    assert cancha["id"] == 2
    assert cancha["activa"] is False


def test_eliminar_cancha_sin_reservas(client):
    nueva_cancha = {
        "nombre": "Cancha Para Eliminar",
        "id_deporte": 2,
        "precio_hora": 900000,
    }

    response_creacion = client.post("/canchas", json=nueva_cancha)

    assert response_creacion.status_code == 201

    response_lista = client.get("/canchas?nombre=Cancha Para Eliminar")

    assert response_lista.status_code == 200

    id_cancha = response_lista.get_json()["canchas"][0]["id"]

    response = client.delete(f"/canchas/{id_cancha}")

    assert response.status_code == 204
    assert response.data == b""

    response_get = client.get(f"/canchas/{id_cancha}")

    assert response_get.status_code == 404


def test_eliminar_cancha_con_reserva_devuelve_409(client):
    reserva = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-12-10T10:00:00.000000-03:00",
        "fecha_hora_fin": "2026-12-10T11:00:00.000000-03:00",
    }

    response_creacion = client.post("/reservas", json=reserva)

    assert response_creacion.status_code == 201

    response = client.delete("/canchas/2")

    assert response.status_code == 409

    response_get = client.get("/canchas/2")

    assert response_get.status_code == 200


def test_eliminar_cancha_inexistente_devuelve_404(client):
    response = client.delete("/canchas/99999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_NO_ENCONTRADO"
    assert data["errors"][0]["message"] == "Cancha no encontrada"
    assert (
        data["errors"][0]["description"]
        == "No se encontró una cancha con el ID indicado."
    )


def test_crear_cancha_rechaza_precio_hora_cero(client):
    nueva_cancha = {
        "nombre": "Cancha Precio Cero",
        "id_deporte": 2,
        "precio_hora": 0,
        "techada": False,
    }

    response = client.post("/canchas", json=nueva_cancha)

    assert response.status_code == 400

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_VALIDACION"


def test_crear_cancha_aplica_valores_por_defecto(client):
    nueva_cancha = {
        "nombre": "Cancha Valores Default",
        "id_deporte": 2,
        "precio_hora": 900000,
    }

    response = client.post("/canchas", json=nueva_cancha)

    assert response.status_code == 201

    response_lista = client.get("/canchas?nombre=Cancha Valores Default")

    assert response_lista.status_code == 200

    cancha = response_lista.get_json()["canchas"][0]

    assert cancha["techada"] is False
    assert cancha["activa"] is True


def test_paginar_canchas_con_limit_y_offset(client):
    response = client.get("/canchas?_limit=1&_offset=1")

    assert response.status_code == 200

    data = response.get_json()

    assert "canchas" in data
    assert len(data["canchas"]) == 1
