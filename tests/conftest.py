import os

import pytest

             
                                                    
                                             
os.environ["DB_NAME"] = "club_encuentro_test"

from app import app
from api_club.db import obtener_conexion


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


@pytest.fixture()
def db():
    conn = obtener_conexion()
    try:
        yield conn
    finally:
        conn.close()


def restaurar_datos_base():
    """
    Deja la BD de test en su estado base.
    Nunca debe ejecutarse sobre la BD de desarrollo.
    """
    assert os.environ["DB_NAME"] == "club_encuentro_test"

    conn = obtener_conexion()
    try:
        cur = conn.cursor()

                                      
        cur.execute("DELETE FROM reservas")
        cur.execute("DELETE FROM bloqueos")
        cur.execute("DELETE FROM canchas WHERE id > 3")

                                                   
        cur.execute("DELETE FROM socios WHERE id > 3")

                                   
        cur.execute(
            """
            UPDATE socios
            SET nombre = CASE id
                WHEN 1 THEN 'Socio Test Uno'
                WHEN 2 THEN 'Socio Test Dos'
                WHEN 3 THEN 'Socio Inactivo'
            END,
            email = CASE id
                WHEN 1 THEN 'test1@example.com'
                WHEN 2 THEN 'test2@example.com'
                WHEN 3 THEN 'inactivo@example.com'
            END,
            activo = CASE id
                WHEN 1 THEN 1
                WHEN 2 THEN 1
                WHEN 3 THEN 0
            END
            WHERE id IN (1, 2, 3)
            """
        )

                                    
        cur.execute(
            """
            UPDATE canchas
            SET nombre = CASE id
                WHEN 1 THEN 'Cancha Test Fútbol'
                WHEN 2 THEN 'Cancha Test Pádel'
                WHEN 3 THEN 'Cancha Inactiva'
            END,
            id_deporte = CASE id
                WHEN 1 THEN 1
                WHEN 2 THEN 2
                WHEN 3 THEN 1
            END,
            precio_hora = CASE id
                WHEN 1 THEN 1200000
                WHEN 2 THEN 750000
                WHEN 3 THEN 500000
            END,
            techada = CASE id
                WHEN 1 THEN 0
                WHEN 2 THEN 1
                WHEN 3 THEN 0
            END,
            activa = CASE id
                WHEN 1 THEN 1
                WHEN 2 THEN 1
                WHEN 3 THEN 0
            END
            WHERE id IN (1, 2, 3)
            """
        )

        conn.commit()
        cur.close()
    finally:
        conn.close()


@pytest.fixture(autouse=True)
def limpiar_datos_test():
                                   
    restaurar_datos_base()

    yield

                                     
    restaurar_datos_base()
