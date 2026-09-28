from api_club.repositories import canchas as repo


def listar_canchas(limit, offset, nombre=None, id_deporte=None, techada=None, activa=None):
    return repo.obtener_todas(limit, offset, nombre, id_deporte, techada, activa)


def contar_canchas(nombre=None, id_deporte=None, techada=None, activa=None):
    return repo.contar_canchas(nombre, id_deporte, techada, activa)


def crear_cancha(nombre, id_deporte, precio_hora, techada, activa):
    if not repo.existe_deporte(id_deporte):
        return None, "DEPORTE_NO_EXISTE"
    return repo.crear_cancha(nombre, id_deporte, precio_hora, techada, activa), None


def obtener_cancha_por_id(id_cancha):
    return repo.obtener_datos_cancha(id_cancha)


def actualizar_cancha(id_cancha, datos):
    if not repo.obtener_datos_cancha(id_cancha):
        return False
    repo.actualizar_cancha(id_cancha, datos)
    return True


def eliminar_cancha(id_cancha):
    if not repo.obtener_datos_cancha(id_cancha):
        return False, "NO_ENCONTRADA"
    if repo.tiene_reservas(id_cancha):
        return False, "TIENE_RESERVAS"
    repo.eliminar_cancha(id_cancha)
    return True, None


def consultar_disponibilidad(fecha, hora_inicio, hora_fin, id_deporte=None, techada=None, limit=10, offset=0):
    return repo.obtener_disponibles(fecha, hora_inicio, hora_fin, id_deporte, techada, limit, offset)


def contar_disponibles(fecha, hora_inicio, hora_fin, id_deporte=None, techada=None):
    return repo.contar_disponibles(fecha, hora_inicio, hora_fin, id_deporte, techada)
