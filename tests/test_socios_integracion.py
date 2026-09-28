def test_crear_socio_normaliza_email(client, db):
    nuevo_socio = {
        "nombre": "Nuevo Socio",
        "email": "  NUEVO.SOCIO@EXAMPLE.COM  ",
    }

    response = client.post("/socios", json=nuevo_socio)

    assert response.status_code == 201

    cur = db.cursor(dictionary=True)
    cur.execute(
        """
        SELECT nombre, email, activo
        FROM socios
        WHERE email = %s
        """,
        ("nuevo.socio@example.com",),
    )
    socio = cur.fetchone()
    cur.close()

    assert socio is not None
    assert socio["nombre"] == "Nuevo Socio"
    assert socio["email"] == "nuevo.socio@example.com"
    assert socio["activo"] in (1, True)


def test_rechaza_email_duplicado_sin_importar_mayusculas(client, db):
    nuevo_socio = {
        "nombre": "Socio Duplicado",
        "email": "  TEST1@EXAMPLE.COM  ",
    }

    response = client.post("/socios", json=nuevo_socio)

    assert response.status_code == 409

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["message"] == "Email duplicado"

                                                                   
    cur = db.cursor()
    cur.execute(
        """
        SELECT COUNT(*)
        FROM socios
        WHERE LOWER(email) = %s
        """,
        ("test1@example.com",),
    )
    cantidad = cur.fetchone()[0]
    cur.close()

    assert cantidad == 1


def test_modificar_nombre_de_socio(client):
    response = client.patch(
        "/socios/1",
        json={"nombre": "Socio Modificado"},
    )

    assert response.status_code == 204
    assert response.data == b""

    response_get = client.get("/socios/1")

    assert response_get.status_code == 200

    socio = response_get.get_json()

    assert socio["id"] == 1
    assert socio["nombre"] == "Socio Modificado"
    assert socio["email"] == "test1@example.com"
    assert socio["activo"] is True


def test_modificar_socio_rechaza_email_duplicado(client, db):
    response = client.patch(
        "/socios/1",
        json={"email": "  TEST2@EXAMPLE.COM  "},
    )

    assert response.status_code == 409

    data = response.get_json()
    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["message"] == "Email duplicado"

                                              
    response_get = client.get("/socios/1")

    assert response_get.status_code == 200

    socio = response_get.get_json()

    assert socio["id"] == 1
    assert socio["nombre"] == "Socio Test Uno"
    assert socio["email"] == "test1@example.com"
    assert socio["activo"] is True

                                                   
    cur = db.cursor(dictionary=True)
    cur.execute(
        """
        SELECT nombre, email, activo
        FROM socios
        WHERE id = 1
        """
    )
    socio_bd = cur.fetchone()
    cur.close()

    assert socio_bd["nombre"] == "Socio Test Uno"
    assert socio_bd["email"] == "test1@example.com"
    assert socio_bd["activo"] in (1, True)


def test_modificar_socio_rechaza_cuerpo_vacio(client):
    response = client.patch(
        "/socios/1",
        json={},
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_VALIDACION"
    assert data["errors"][0]["message"] == "Datos inválidos"
    assert data["errors"][0]["description"] == "El cuerpo no puede estar vacío"

                                      
    response_get = client.get("/socios/1")

    assert response_get.status_code == 200

    socio = response_get.get_json()

    assert socio["nombre"] == "Socio Test Uno"
    assert socio["email"] == "test1@example.com"
    assert socio["activo"] is True


def test_modificar_socio_rechaza_campo_desconocido(client):
    response = client.patch(
        "/socios/1",
        json={"dni": "12345678"},
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_VALIDACION"
    assert data["errors"][0]["message"] == "Datos inválidos"
    assert data["errors"][0]["description"] == "Campo(s) desconocido(s): dni"

                                      
    response_get = client.get("/socios/1")

    assert response_get.status_code == 200

    socio = response_get.get_json()

    assert socio["nombre"] == "Socio Test Uno"
    assert socio["email"] == "test1@example.com"
    assert socio["activo"] is True


def test_modificar_socio_inexistente_devuelve_404(client):
    response = client.patch(
        "/socios/99999",
        json={"nombre": "No existe"},
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_NO_ENCONTRADO"
    assert data["errors"][0]["message"] == "Socio no encontrado"
    assert (
        data["errors"][0]["description"]
        == "No se encontró un socio con el ID indicado"
    )


def test_buscar_socio_por_nombre_es_parcial_e_insensible_a_mayusculas(client):
    response = client.get("/socios?nombre=tEsT uNo")

    assert response.status_code == 200

    data = response.get_json()

    assert "socios" in data
    assert len(data["socios"]) == 1

    socio = data["socios"][0]

    assert socio["id"] == 1
    assert socio["nombre"] == "Socio Test Uno"
    assert socio["email"] == "test1@example.com"
    assert socio["activo"] is True


def test_filtrar_socios_activos(client):
    response = client.get("/socios?activo=true")

    assert response.status_code == 200

    data = response.get_json()
    socios = data["socios"]

    ids = {socio["id"] for socio in socios}

    assert ids == {1, 2}
    assert all(socio["activo"] is True for socio in socios)


def test_filtrar_socios_inactivos(client):
    response = client.get("/socios?activo=false")

    assert response.status_code == 200

    data = response.get_json()
    socios = data["socios"]

    assert len(socios) == 1
    assert socios[0]["id"] == 3
    assert socios[0]["nombre"] == "Socio Inactivo"
    assert socios[0]["activo"] is False


def test_filtrar_socios_rechaza_booleano_invalido(client):
    response = client.get("/socios?activo=1")

    assert response.status_code == 400

    data = response.get_json()

    assert data["errors"][0]["code"] == "ERROR_VALIDACION"
    assert data["errors"][0]["message"] == "El parámetro activo debe ser true o false"
