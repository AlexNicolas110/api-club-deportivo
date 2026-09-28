from api_club.db import obtener_conexion


def convertir_cancha(cancha):
    if cancha:
        cancha["techada"] = bool(cancha["techada"])
        cancha["activa"] = bool(cancha["activa"])
    return cancha


def obtener_todas(limit, offset, nombre=None, id_deporte=None, techada=None, activa=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    consulta = "SELECT id,nombre,id_deporte,precio_hora,techada,activa FROM canchas"
    condiciones = []
    parametros = []
    if nombre is not None:
        condiciones.append("LOWER(nombre) LIKE LOWER(%s)")
        parametros.append(f"%{nombre}%")
    if id_deporte is not None:
        condiciones.append("id_deporte = %s")
        parametros.append(id_deporte)
    if techada is not None:
        condiciones.append("techada = %s")
        parametros.append(techada)
    if activa is not None:
        condiciones.append("activa = %s")
        parametros.append(activa)
    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)
    consulta += " ORDER BY id ASC LIMIT %s OFFSET %s"
    parametros.extend([limit, offset])
    cursor.execute(consulta, parametros)
    canchas = [convertir_cancha(cancha) for cancha in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return canchas


def contar_canchas(nombre=None, id_deporte=None, techada=None, activa=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT COUNT(*) FROM canchas"
    condiciones = []
    parametros = []
    if nombre is not None:
        condiciones.append("LOWER(nombre) LIKE LOWER(%s)")
        parametros.append(f"%{nombre}%")
    if id_deporte is not None:
        condiciones.append("id_deporte = %s")
        parametros.append(id_deporte)
    if techada is not None:
        condiciones.append("techada = %s")
        parametros.append(techada)
    if activa is not None:
        condiciones.append("activa = %s")
        parametros.append(activa)
    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)
    cursor.execute(consulta, parametros)
    total = cursor.fetchone()[0]
    cursor.close()
    conexion.close()
    return total


def obtener_disponibles(fecha, hora_inicio, hora_fin, id_deporte=None, techada=None, limit=10, offset=0):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    consulta = """
        SELECT c.id,c.nombre,c.id_deporte,c.precio_hora,c.techada,c.activa
        FROM canchas c
        WHERE c.activa = TRUE
    """
    parametros = []
    if id_deporte is not None:
        consulta += " AND c.id_deporte = %s"
        parametros.append(id_deporte)
    if techada is not None:
        consulta += " AND c.techada = %s"
        parametros.append(techada)
    consulta += """
        AND NOT EXISTS (
            SELECT 1 FROM reservas r
            WHERE r.id_cancha = c.id
              AND r.estado = 'confirmada'
              AND r.fecha_hora_inicio < TIMESTAMP(%s, %s)
              AND r.fecha_hora_fin > TIMESTAMP(%s, %s)
        )
        AND NOT EXISTS (
            SELECT 1 FROM bloqueos b
            WHERE b.id_cancha = c.id
              AND b.fecha = %s
              AND b.hora_inicio < %s
              AND b.hora_fin > %s
        )
        ORDER BY c.id ASC LIMIT %s OFFSET %s
    """
    parametros.extend([fecha, hora_fin, fecha, hora_inicio, fecha, hora_fin, hora_inicio, limit, offset])
    cursor.execute(consulta, parametros)
    canchas = [convertir_cancha(cancha) for cancha in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return canchas


def contar_disponibles(fecha, hora_inicio, hora_fin, id_deporte=None, techada=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT COUNT(*) FROM canchas c WHERE c.activa = TRUE"
    parametros = []
    if id_deporte is not None:
        consulta += " AND c.id_deporte = %s"
        parametros.append(id_deporte)
    if techada is not None:
        consulta += " AND c.techada = %s"
        parametros.append(techada)
    consulta += """
        AND NOT EXISTS (
            SELECT 1 FROM reservas r
            WHERE r.id_cancha = c.id
              AND r.estado = 'confirmada'
              AND r.fecha_hora_inicio < TIMESTAMP(%s, %s)
              AND r.fecha_hora_fin > TIMESTAMP(%s, %s)
        )
        AND NOT EXISTS (
            SELECT 1 FROM bloqueos b
            WHERE b.id_cancha = c.id
              AND b.fecha = %s
              AND b.hora_inicio < %s
              AND b.hora_fin > %s
        )
    """
    parametros.extend([fecha, hora_fin, fecha, hora_inicio, fecha, hora_fin, hora_inicio])
    cursor.execute(consulta, parametros)
    total = cursor.fetchone()[0]
    cursor.close()
    conexion.close()
    return total


def existe_deporte(id_deporte):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT 1 FROM deportes WHERE id = %s", (id_deporte,))
    existe = cursor.fetchone() is not None
    cursor.close()
    conexion.close()
    return existe


def crear_cancha(nombre, id_deporte, precio_hora, techada, activa):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO canchas(nombre,id_deporte,precio_hora,techada,activa) VALUES(%s,%s,%s,%s,%s)",
        (nombre, id_deporte, precio_hora, techada, activa),
    )
    conexion.commit()
    id_nueva = cursor.lastrowid
    cursor.close()
    conexion.close()
    return id_nueva


def obtener_datos_cancha(id_cancha):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id,nombre,id_deporte,precio_hora,techada,activa FROM canchas WHERE id = %s", (id_cancha,))
    cancha = convertir_cancha(cursor.fetchone())
    cursor.close()
    conexion.close()
    return cancha


def actualizar_cancha(id_cancha, datos):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    campos = []
    valores = []
    for campo in ("nombre", "precio_hora", "techada", "activa"):
        if campo in datos:
            campos.append(f"{campo} = %s")
            valores.append(datos[campo])
    valores.append(id_cancha)
    cursor.execute(f"UPDATE canchas SET {', '.join(campos)} WHERE id = %s", valores)
    conexion.commit()
    cursor.close()
    conexion.close()


def tiene_reservas(id_cancha):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM reservas WHERE id_cancha = %s", (id_cancha,))
    tiene = cursor.fetchone()[0] > 0
    cursor.close()
    conexion.close()
    return tiene


def eliminar_cancha(id_cancha):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM canchas WHERE id = %s", (id_cancha,))
    conexion.commit()
    cursor.close()
    conexion.close()
