from api_club.db import obtener_conexion


def convertir_socio(socio):
    if socio:
        socio["activo"] = bool(socio["activo"])
    return socio


def get_socios(limit, offset, nombre=None, activo=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    consulta = "SELECT id,nombre,email,activo FROM socios WHERE 1=1"
    parametros = []
    if nombre is not None:
        consulta += " AND LOWER(nombre) LIKE LOWER(%s)"
        parametros.append(f"%{nombre}%")
    if activo is not None:
        consulta += " AND activo = %s"
        parametros.append(activo)
    consulta += " ORDER BY id ASC LIMIT %s OFFSET %s"
    parametros.extend([limit, offset])
    cursor.execute(consulta, parametros)
    socios = [convertir_socio(socio) for socio in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return socios


def contar_socios(nombre=None, activo=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT COUNT(*) FROM socios WHERE 1=1"
    parametros = []
    if nombre is not None:
        consulta += " AND LOWER(nombre) LIKE LOWER(%s)"
        parametros.append(f"%{nombre}%")
    if activo is not None:
        consulta += " AND activo = %s"
        parametros.append(activo)
    cursor.execute(consulta, parametros)
    total = cursor.fetchone()[0]
    cursor.close()
    conexion.close()
    return total


def obtener_por_id(id_socio):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id,nombre,email,activo FROM socios WHERE id = %s", (id_socio,))
    socio = convertir_socio(cursor.fetchone())
    cursor.close()
    conexion.close()
    return socio


def existe_email(email, excluir_id=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT 1 FROM socios WHERE email = %s"
    parametros = [email]
    if excluir_id is not None:
        consulta += " AND id != %s"
        parametros.append(excluir_id)
    cursor.execute(consulta, parametros)
    existe = cursor.fetchone() is not None
    cursor.close()
    conexion.close()
    return existe


def crear_socio(nombre, email):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO socios(nombre,email,activo) VALUES(%s,%s,TRUE)", (nombre, email))
    conexion.commit()
    id_nuevo = cursor.lastrowid
    cursor.close()
    conexion.close()
    return id_nuevo


def actualizar_socio(id_socio, campos):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    columnas = ", ".join(f"{campo} = %s" for campo in campos)
    valores = list(campos.values()) + [id_socio]
    cursor.execute(f"UPDATE socios SET {columnas} WHERE id = %s", valores)
    conexion.commit()
    cursor.close()
    conexion.close()
