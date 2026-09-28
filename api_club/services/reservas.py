from datetime import datetime, timedelta, timezone
from api_club.db import obtener_conexion
from api_club.repositories import reservas as repo


TZ = timezone(timedelta(hours=-3))


def listar_reservas(limit, offset, **filtros):
    return repo.obtener_todas(limit, offset, **filtros)


def contar_reservas(**filtros):
    return repo.contar_reservas(**filtros)


def obtener(id_reserva):
    return repo.obtener_por_id(id_reserva)


def validar_entidades(id_socio, id_cancha, conexion):
    socio = repo.obtener_socio(id_socio, conexion)
    cancha = repo.obtener_cancha(id_cancha, conexion)
    if not socio:
        return None, None, "SOCIO_NO_EXISTE"
    if not cancha:
        return None, None, "CANCHA_NO_EXISTE"
    if not socio["activo"]:
        return None, None, "SOCIO_INACTIVO"
    if not cancha["activa"]:
        return None, None, "CANCHA_INACTIVA"
    return socio, cancha, None


def crear(id_socio, id_cancha, inicio, fin, horas):
    conexion = obtener_conexion()
    try:
        conexion.start_transaction()
        _, cancha, motivo = validar_entidades(id_socio, id_cancha, conexion)
        if motivo:
            return None, motivo
        inicio_db = inicio.replace(tzinfo=None)
        fin_db = fin.replace(tzinfo=None)
        cancha_ocupada, socio_ocupado = repo.hay_superposicion(id_cancha, id_socio, inicio_db, fin_db, conexion)
        if cancha_ocupada:
            return None, "CANCHA_OCUPADA"
        if socio_ocupado:
            return None, "SOCIO_OCUPADO"
        if repo.hay_bloqueo(id_cancha, inicio_db, fin_db, conexion):
            return None, "CANCHA_BLOQUEADA"
        precio_hora = cancha["precio_hora"]
        id_reserva = repo.insertar(id_socio, id_cancha, inicio, fin, precio_hora, precio_hora * horas, conexion)
        conexion.commit()
        return id_reserva, None
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def cambiar_estado(id_reserva, nuevo_estado):
    conexion = obtener_conexion()
    try:
        conexion.start_transaction()
        reserva = repo.obtener_por_id(id_reserva, conexion)
        if not reserva:
            return "NO_EXISTE"
        estado_actual = reserva["estado"]
        if nuevo_estado == estado_actual:
            conexion.commit()
            return None
        if estado_actual != "confirmada":
            return "TRANSICION_INVALIDA"
        inicio = datetime.fromisoformat(reserva["fecha_hora_inicio"])
        fin = datetime.fromisoformat(reserva["fecha_hora_fin"])
        ahora = datetime.now(TZ)
        if nuevo_estado == "cancelada" and ahora >= inicio:
            return "TRANSICION_INVALIDA"
        if nuevo_estado == "finalizada" and ahora < fin:
            return "TRANSICION_INVALIDA"
        if nuevo_estado not in {"cancelada", "finalizada"}:
            return "TRANSICION_INVALIDA"
        repo.actualizar_estado(id_reserva, nuevo_estado, conexion)
        conexion.commit()
        return None
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def crear_recurrentes(id_socio, id_cancha, inicio, fin, horas, cantidad):
    conexion = obtener_conexion()
    conflictos = []
    ids = []
    try:
        conexion.start_transaction()
        _, cancha, motivo = validar_entidades(id_socio, id_cancha, conexion)
        if motivo:
            return None, motivo, None
        for semana in range(cantidad):
            inicio_semana = inicio + timedelta(weeks=semana)
            fin_semana = fin + timedelta(weeks=semana)
            inicio_db = inicio_semana.replace(tzinfo=None)
            fin_db = fin_semana.replace(tzinfo=None)
            cancha_ocupada, socio_ocupado = repo.hay_superposicion(id_cancha, id_socio, inicio_db, fin_db, conexion)
            bloqueada = repo.hay_bloqueo(id_cancha, inicio_db, fin_db, conexion)
            if cancha_ocupada or socio_ocupado or bloqueada:
                conflictos.append(inicio_semana.strftime("%Y-%m-%d"))
        if conflictos:
            return None, "CONFLICTO", conflictos
        precio_hora = cancha["precio_hora"]
        for semana in range(cantidad):
            inicio_semana = inicio + timedelta(weeks=semana)
            fin_semana = fin + timedelta(weeks=semana)
            id_reserva = repo.insertar(id_socio, id_cancha, inicio_semana, fin_semana, precio_hora, precio_hora * horas, conexion)
            ids.append(id_reserva)
        conexion.commit()
        return ids, None, None
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
