def test_crear_reserva_guarda_snapshot_del_precio(client, db):
    payload = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-10-20T10:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-20T12:00:00.000000-03:00",
    }

    response = client.post("/reservas", json=payload)

    assert response.status_code == 201
    assert response.data == b""

    cur = db.cursor(dictionary=True)
    cur.execute(
        """
        SELECT
            id_socio,
            id_cancha,
            precio_hora,
            precio_total,
            estado
        FROM reservas
        """
    )
    reserva = cur.fetchone()
    cur.close()

    assert reserva is not None
    assert reserva["id_socio"] == 1
    assert reserva["id_cancha"] == 2
    assert reserva["precio_hora"] == 750000
    assert reserva["precio_total"] == 1500000
    assert reserva["estado"] == "confirmada"


def test_rechaza_solapamiento_en_misma_cancha(client, db):
    primera = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-10-21T10:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-21T12:00:00.000000-03:00",
    }

    conflicto = {
        "id_socio": 2,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-10-21T11:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-21T12:00:00.000000-03:00",
    }

    response_1 = client.post("/reservas", json=primera)
    assert response_1.status_code == 201

    response_2 = client.post("/reservas", json=conflicto)

    assert response_2.status_code == 409

    data = response_2.get_json()
    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["description"] == "CANCHA_OCUPADA"

                                                                     
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM reservas")
    cantidad = cur.fetchone()[0]
    cur.close()

    assert cantidad == 1


def test_rechaza_socio_ocupado_en_otra_cancha(client, db):
    primera = {
        "id_socio": 1,
        "id_cancha": 1,
        "fecha_hora_inicio": "2026-10-22T18:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-22T20:00:00.000000-03:00",
    }

    conflicto = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-10-22T19:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-22T20:00:00.000000-03:00",
    }

    response_1 = client.post("/reservas", json=primera)
    assert response_1.status_code == 201

    response_2 = client.post("/reservas", json=conflicto)

    assert response_2.status_code == 409

    data = response_2.get_json()
    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["description"] == "SOCIO_OCUPADO"

                                                      
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM reservas")
    cantidad = cur.fetchone()[0]
    cur.close()

    assert cantidad == 1


def test_permite_reservas_consecutivas_en_misma_cancha(client, db):
    primera = {
        "id_socio": 1,
        "id_cancha": 1,
        "fecha_hora_inicio": "2026-10-23T18:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-23T20:00:00.000000-03:00",
    }

    consecutiva = {
        "id_socio": 2,
        "id_cancha": 1,
        "fecha_hora_inicio": "2026-10-23T20:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-23T21:00:00.000000-03:00",
    }

    response_1 = client.post("/reservas", json=primera)
    assert response_1.status_code == 201

    response_2 = client.post("/reservas", json=consecutiva)
    assert response_2.status_code == 201

    cur = db.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin
        FROM reservas
        ORDER BY fecha_hora_inicio
        """
    )
    reservas = cur.fetchall()
    cur.close()

    assert len(reservas) == 2
    assert reservas[0]["id_socio"] == 1
    assert reservas[1]["id_socio"] == 2

                                                                
    assert reservas[0]["fecha_hora_fin"] == reservas[1]["fecha_hora_inicio"]


def test_rechaza_reserva_si_cancha_esta_bloqueada(client, db):
    bloqueo = {
        "id_cancha": 2,
        "fecha": "2026-10-24",
        "hora_inicio": "10:00:00",
        "hora_fin": "12:00:00",
        "motivo": "Mantenimiento",
    }

    response_bloqueo = client.post("/bloqueos", json=bloqueo)
    assert response_bloqueo.status_code == 201

    reserva = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-10-24T11:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-24T12:00:00.000000-03:00",
    }

    response = client.post("/reservas", json=reserva)

    assert response.status_code == 409

    data = response.get_json()
    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["description"] == "CANCHA_BLOQUEADA"

                                                  
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM reservas")
    cantidad_reservas = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bloqueos")
    cantidad_bloqueos = cur.fetchone()[0]
    cur.close()

    assert cantidad_reservas == 0
    assert cantidad_bloqueos == 1


def test_rechaza_reserva_de_socio_inactivo(client, db):
    reserva = {
        "id_socio": 3,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-10-26T10:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-26T11:00:00.000000-03:00",
    }

    response = client.post("/reservas", json=reserva)

    assert response.status_code == 409

    data = response.get_json()
    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["description"] == "SOCIO_INACTIVO"

    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM reservas")
    cantidad = cur.fetchone()[0]
    cur.close()

    assert cantidad == 0


def test_rechaza_reserva_en_cancha_inactiva(client, db):
    reserva = {
        "id_socio": 1,
        "id_cancha": 3,
        "fecha_hora_inicio": "2026-10-26T12:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-26T13:00:00.000000-03:00",
    }

    response = client.post("/reservas", json=reserva)

    assert response.status_code == 409

    data = response.get_json()
    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["description"] == "CANCHA_INACTIVA"

    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM reservas")
    cantidad = cur.fetchone()[0]
    cur.close()

    assert cantidad == 0


def test_recurrentes_con_conflicto_no_insertan_parcialmente(client, db):
                                                             
    existente = {
        "id_socio": 2,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-11-02T15:00:00.000000-03:00",
        "fecha_hora_fin": "2026-11-02T16:00:00.000000-03:00",
    }

    response_existente = client.post("/reservas", json=existente)
    assert response_existente.status_code == 201

                         
                    
                        
                    
    serie = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-10-26T15:00:00.000000-03:00",
        "fecha_hora_fin": "2026-10-26T16:00:00.000000-03:00",
        "cantidad_semanas": 3,
    }

    response = client.post("/reservas/recurrentes", json=serie)

    assert response.status_code == 409

    data = response.get_json()
    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["message"] == "Serie con conflictos"
    assert "2026-11-02" in data["conflictos"]

                                                                  
                                                       
    cur = db.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin
        FROM reservas
        ORDER BY fecha_hora_inicio
        """
    )
    reservas = cur.fetchall()
    cur.close()

    assert len(reservas) == 1
    assert reservas[0]["id_socio"] == 2
    assert reservas[0]["id_cancha"] == 2
    assert reservas[0]["fecha_hora_inicio"].strftime(
        "%Y-%m-%d %H:%M:%S"
    ) == "2026-11-02 15:00:00"


def test_crear_recurrentes_genera_toda_la_serie(client, db):
    serie = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-11-16T15:00:00.000000-03:00",
        "fecha_hora_fin": "2026-11-16T16:00:00.000000-03:00",
        "cantidad_semanas": 3,
    }

    response = client.post("/reservas/recurrentes", json=serie)

    assert response.status_code == 201
    assert response.data == b""

    cur = db.cursor(dictionary=True)
    cur.execute(
        """
        SELECT
            id_socio,
            id_cancha,
            fecha_hora_inicio,
            fecha_hora_fin,
            precio_hora,
            precio_total,
            estado
        FROM reservas
        ORDER BY fecha_hora_inicio
        """
    )
    reservas = cur.fetchall()
    cur.close()

    assert len(reservas) == 3

    fechas_esperadas = [
        "2026-11-16 15:00:00",
        "2026-11-23 15:00:00",
        "2026-11-30 15:00:00",
    ]

    assert [
        r["fecha_hora_inicio"].strftime("%Y-%m-%d %H:%M:%S")
        for r in reservas
    ] == fechas_esperadas

    for reserva in reservas:
        assert reserva["id_socio"] == 1
        assert reserva["id_cancha"] == 2
        assert reserva["precio_hora"] == 750000
        assert reserva["precio_total"] == 750000
        assert reserva["estado"] == "confirmada"

                                                          
        assert (
            reserva["fecha_hora_fin"] - reserva["fecha_hora_inicio"]
        ).total_seconds() == 3600


def test_reserva_confirmada_puede_cancelarse(client, db):
    reserva = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-12-01T10:00:00.000000-03:00",
        "fecha_hora_fin": "2026-12-01T11:00:00.000000-03:00",
    }

    response_creacion = client.post("/reservas", json=reserva)
    assert response_creacion.status_code == 201

    cur = db.cursor()
    cur.execute("SELECT id FROM reservas")
    id_reserva = cur.fetchone()[0]
    cur.close()

    response = client.put(
        f"/reservas/{id_reserva}/estado",
        json={"estado": "cancelada"},
    )

    assert response.status_code == 204
    assert response.data == b""

    response_get = client.get(f"/reservas/{id_reserva}")

    assert response_get.status_code == 200

    resultado = response_get.get_json()

    assert resultado["estado"] == "cancelada"


def test_reserva_cancelada_no_puede_reactivarse(client, db):
    reserva = {
        "id_socio": 1,
        "id_cancha": 2,
        "fecha_hora_inicio": "2026-12-02T10:00:00.000000-03:00",
        "fecha_hora_fin": "2026-12-02T11:00:00.000000-03:00",
    }

    response_creacion = client.post("/reservas", json=reserva)
    assert response_creacion.status_code == 201

    cur = db.cursor()
    cur.execute("SELECT id FROM reservas")
    id_reserva = cur.fetchone()[0]
    cur.close()

                            
    response_cancelar = client.put(
        f"/reservas/{id_reserva}/estado",
        json={"estado": "cancelada"},
    )
    assert response_cancelar.status_code == 204

                                   
    response_reactivar = client.put(
        f"/reservas/{id_reserva}/estado",
        json={"estado": "confirmada"},
    )

    assert response_reactivar.status_code == 409

    data = response_reactivar.get_json()
    assert data["errors"][0]["code"] == "ERROR_CONFLICTO"
    assert data["errors"][0]["message"] == "Transición no permitida"

                                               
    response_get = client.get(f"/reservas/{id_reserva}")
    assert response_get.status_code == 200

    resultado = response_get.get_json()
    assert resultado["estado"] == "cancelada"


def test_reserva_finalizada_no_puede_cambiar_estado(client, db):
                                                                  
                                             
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO reservas
        (
            id_socio,
            id_cancha,
            fecha_hora_inicio,
            fecha_hora_fin,
            precio_hora,
            precio_total,
            estado
        )
        VALUES
        (
            1,
            2,
            '2026-09-20 10:00:00',
            '2026-09-20 11:00:00',
            750000,
            750000,
            'confirmada'
        )
        """
    )
    db.commit()
    id_reserva = cur.lastrowid
    cur.close()

                                                                     
    response_finalizar = client.put(
        f"/reservas/{id_reserva}/estado",
        json={"estado": "finalizada"},
    )

    assert response_finalizar.status_code == 204

    response_get = client.get(f"/reservas/{id_reserva}")
    assert response_get.status_code == 200
    assert response_get.get_json()["estado"] == "finalizada"

                                                 
    response_cancelar = client.put(
        f"/reservas/{id_reserva}/estado",
        json={"estado": "cancelada"},
    )

    assert response_cancelar.status_code == 409

                                        
    response_confirmar = client.put(
        f"/reservas/{id_reserva}/estado",
        json={"estado": "confirmada"},
    )

    assert response_confirmar.status_code == 409

                                        
    response_final = client.get(f"/reservas/{id_reserva}")
    assert response_final.status_code == 200
    assert response_final.get_json()["estado"] == "finalizada"
