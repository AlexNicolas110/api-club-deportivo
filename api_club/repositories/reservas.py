from api_club.db import obtener_conexion
from api_club.utils import fecha_hora_api


CAMPOS = "id,id_cancha,id_socio,fecha_hora_inicio,fecha_hora_fin,estado,precio_hora,precio_total"


def convertir_reserva(reserva):
    if reserva:
        reserva["fecha_hora_inicio"] = fecha_hora_api(reserva["fecha_hora_inicio"])
        reserva["fecha_hora_fin"] = fecha_hora_api(reserva["fecha_hora_fin"])
    return reserva


def obtener_todas(limit, offset, id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    consulta = f"SELECT {CAMPOS} FROM reservas WHERE 1=1"
    parametros = []
    if id_cancha is not None:
        consulta += " AND id_cancha = %s"
        parametros.append(id_cancha)
    if id_socio is not None:
        consulta += " AND id_socio = %s"
        parametros.append(id_socio)
    if estado is not None:
        consulta += " AND estado = %s"
        parametros.append(estado)
    if fecha_desde is not None:
        consulta += " AND DATE(fecha_hora_inicio) >= %s"
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        consulta += " AND DATE(fecha_hora_inicio) <= %s"
        parametros.append(fecha_hasta)
    consulta += " ORDER BY id ASC LIMIT %s OFFSET %s"
    parametros.extend([limit, offset])
    cursor.execute(consulta, parametros)
    reservas = [convertir_reserva(reserva) for reserva in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return reservas


def contar_reservas(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT COUNT(*) FROM reservas WHERE 1=1"
    parametros = []
    if id_cancha is not None:
        consulta += " AND id_cancha = %s"
        parametros.append(id_cancha)
    if id_socio is not None:
        consulta += " AND id_socio = %s"
        parametros.append(id_socio)
    if estado is not None:
        consulta += " AND estado = %s"
        parametros.append(estado)
    if fecha_desde is not None:
        consulta += " AND DATE(fecha_hora_inicio) >= %s"
        parametros.append(fecha_desde)
    if fecha_hasta is not None:
        consulta += " AND DATE(fecha_hora_inicio) <= %s"
        parametros.append(fecha_hasta)
    cursor.execute(consulta, parametros)
    total = cursor.fetchone()[0]
    cursor.close()
    conexion.close()
    return total


def obtener_por_id(id_reserva, conexion=None):
    propia = conexion is None
    conexion = conexion or obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(f"SELECT {CAMPOS} FROM reservas WHERE id = %s", (id_reserva,))
    reserva = convertir_reserva(cursor.fetchone())
    cursor.close()
    if propia:
        conexion.close()
    return reserva


def obtener_socio(id_socio, conexion):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id,activo FROM socios WHERE id = %s", (id_socio,))
    socio = cursor.fetchone()
    cursor.close()
    return socio


def obtener_cancha(id_cancha, conexion):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id,precio_hora,activa FROM canchas WHERE id = %s", (id_cancha,))
    cancha = cursor.fetchone()
    cursor.close()
    return cancha


def hay_superposicion(id_cancha, id_socio, inicio, fin, conexion):
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT id_cancha,id_socio FROM reservas
        WHERE estado = 'confirmada'
          AND fecha_hora_inicio < %s
          AND fecha_hora_fin > %s
          AND (id_cancha = %s OR id_socio = %s)
        """,
        (fin, inicio, id_cancha, id_socio),
    )
    filas = cursor.fetchall()
    cursor.close()
    cancha_ocupada = any(fila[0] == id_cancha for fila in filas)
    socio_ocupado = any(fila[1] == id_socio for fila in filas)
    return cancha_ocupada, socio_ocupado


def hay_bloqueo(id_cancha, inicio, fin, conexion):
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) FROM bloqueos
        WHERE id_cancha = %s
          AND TIMESTAMP(fecha,hora_inicio) < %s
          AND TIMESTAMP(fecha,hora_fin) > %s
        """,
        (id_cancha, fin, inicio),
    )
    hay = cursor.fetchone()[0] > 0
    cursor.close()
    return hay


def insertar(id_socio, id_cancha, inicio, fin, precio_hora, precio_total, conexion):
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO reservas(id_socio,id_cancha,fecha_hora_inicio,fecha_hora_fin,precio_hora,precio_total,estado)
        VALUES(%s,%s,%s,%s,%s,%s,'confirmada')
        """,
        (id_socio, id_cancha, inicio.replace(tzinfo=None), fin.replace(tzinfo=None), precio_hora, precio_total),
    )
    id_reserva = cursor.lastrowid
    cursor.close()
    return id_reserva


def actualizar_estado(id_reserva, estado, conexion):
    cursor = conexion.cursor()
    cursor.execute("UPDATE reservas SET estado = %s WHERE id = %s", (estado, id_reserva))
    cursor.close()
