from api_club.db import obtener_conexion


def convertir_hora(valor):
    segundos = int(valor.total_seconds())
    return f"{segundos // 3600:02d}:{(segundos % 3600) // 60:02d}:{segundos % 60:02d}"


def listar(limit, offset, id_cancha=None, fecha=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    consulta = "SELECT id,id_cancha,fecha,hora_inicio,hora_fin,motivo FROM bloqueos WHERE 1=1"
    parametros = []
    if id_cancha is not None:
        consulta += " AND id_cancha = %s"
        parametros.append(id_cancha)
    if fecha is not None:
        consulta += " AND fecha = %s"
        parametros.append(fecha)
    consulta += " ORDER BY id ASC LIMIT %s OFFSET %s"
    parametros.extend([limit, offset])
    cursor.execute(consulta, parametros)
    bloqueos = cursor.fetchall()
    cursor.close()
    conexion.close()
    for bloqueo in bloqueos:
        bloqueo["fecha"] = bloqueo["fecha"].isoformat()
        bloqueo["hora_inicio"] = convertir_hora(bloqueo["hora_inicio"])
        bloqueo["hora_fin"] = convertir_hora(bloqueo["hora_fin"])
    return bloqueos


def contar(id_cancha=None, fecha=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT COUNT(*) FROM bloqueos WHERE 1=1"
    parametros = []
    if id_cancha is not None:
        consulta += " AND id_cancha = %s"
        parametros.append(id_cancha)
    if fecha is not None:
        consulta += " AND fecha = %s"
        parametros.append(fecha)
    cursor.execute(consulta, parametros)
    total = cursor.fetchone()[0]
    cursor.close()
    conexion.close()
    return total


def crear(id_cancha, fecha, inicio, fin, motivo):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT 1 FROM canchas WHERE id = %s", (id_cancha,))
        if not cursor.fetchone():
            return None, "CANCHA_NO_EXISTE"
        cursor.execute(
            """
            SELECT COUNT(*) FROM reservas
            WHERE id_cancha = %s AND estado = 'confirmada'
              AND fecha_hora_inicio < TIMESTAMP(%s,%s)
              AND fecha_hora_fin > TIMESTAMP(%s,%s)
            """,
            (id_cancha, fecha, fin, fecha, inicio),
        )
        if cursor.fetchone()[0]:
            return None, "RESERVA_SUPERPUESTA"
        cursor.execute(
            "SELECT COUNT(*) FROM bloqueos WHERE id_cancha = %s AND fecha = %s AND hora_inicio < %s AND hora_fin > %s",
            (id_cancha, fecha, fin, inicio),
        )
        if cursor.fetchone()[0]:
            return None, "BLOQUEO_SUPERPUESTO"
        cursor.execute(
            "INSERT INTO bloqueos(id_cancha,fecha,hora_inicio,hora_fin,motivo) VALUES(%s,%s,%s,%s,%s)",
            (id_cancha, fecha, inicio, fin, motivo),
        )
        conexion.commit()
        return cursor.lastrowid, None
    finally:
        cursor.close()
        conexion.close()


def eliminar(id_bloqueo):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM bloqueos WHERE id = %s", (id_bloqueo,))
    eliminado = cursor.rowcount > 0
    conexion.commit()
    cursor.close()
    conexion.close()
    return eliminado
