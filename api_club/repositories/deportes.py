from api_club.db import obtener_conexion


def obtener_todos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre FROM deportes ORDER BY id ASC")
    deportes = cursor.fetchall()
    cursor.close()
    conexion.close()
    return deportes
