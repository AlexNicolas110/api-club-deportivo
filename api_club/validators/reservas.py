import re
from datetime import datetime, timedelta, timezone


PATRON_FECHA_HORA = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00$")
TZ = timezone(timedelta(hours=-3))
ESTADOS = {"confirmada", "cancelada", "finalizada"}


def parse_fecha_hora(valor, campo):
    if not isinstance(valor, str) or not PATRON_FECHA_HORA.fullmatch(valor):
        raise ValueError(f"{campo} debe usar el formato YYYY-MM-DDTHH:MM:SS.ffffff-03:00")
    try:
        fecha_hora = datetime.fromisoformat(valor)
    except ValueError:
        raise ValueError(f"{campo} no es una fecha y hora válida")
    if fecha_hora.utcoffset() != timedelta(hours=-3):
        raise ValueError(f"{campo} debe usar GMT-3")
    return fecha_hora


def validar_intervalo(inicio, fin):
    if inicio >= fin:
        raise ValueError("fecha_hora_inicio debe ser anterior a fecha_hora_fin")
    if inicio.date() != fin.date():
        raise ValueError("La reserva no puede atravesar la medianoche")
    if inicio.minute or inicio.second or inicio.microsecond or fin.minute or fin.second or fin.microsecond:
        raise ValueError("Las reservas deben comenzar y terminar en horas en punto")
    if inicio.hour < 8 or fin.hour > 23:
        raise ValueError("El intervalo debe estar dentro del horario 08:00 a 23:00")
    horas = int((fin - inicio).total_seconds() / 3600)
    if horas < 1 or horas > 3:
        raise ValueError("La reserva debe durar entre 1 y 3 horas completas")
    if inicio <= datetime.now(TZ):
        raise ValueError("La reserva debe comenzar en el futuro")
    return horas


def validar_creacion(datos):
    if not isinstance(datos, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")
    permitidos = {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        raise ValueError(f"Campo(s) desconocido(s): {', '.join(sorted(desconocidos))}")
    faltantes = permitidos - set(datos)
    if faltantes:
        raise ValueError(f"Falta(n) campo(s) obligatorio(s): {', '.join(sorted(faltantes))}")
    for campo in ("id_socio", "id_cancha"):
        valor = datos[campo]
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 1:
            raise ValueError(f"{campo} debe ser un entero positivo")
    inicio = parse_fecha_hora(datos["fecha_hora_inicio"], "fecha_hora_inicio")
    fin = parse_fecha_hora(datos["fecha_hora_fin"], "fecha_hora_fin")
    horas = validar_intervalo(inicio, fin)
    return datos["id_socio"], datos["id_cancha"], inicio, fin, horas


def validar_estado(datos):
    if not isinstance(datos, dict) or set(datos) != {"estado"}:
        raise ValueError("El cuerpo debe contener únicamente el campo estado")
    if datos["estado"] not in ESTADOS:
        raise ValueError("estado debe ser confirmada, cancelada o finalizada")
    return datos["estado"]


def validar_filtros(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None):
    resultado = {
        "id_cancha": None,
        "id_socio": None,
        "estado": estado,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    }
    for campo, valor in (("id_cancha", id_cancha), ("id_socio", id_socio)):
        if valor is not None:
            try:
                numero = int(valor)
            except ValueError:
                raise ValueError(f"{campo} debe ser un número entero")
            if numero < 1:
                raise ValueError(f"{campo} debe ser un número positivo")
            resultado[campo] = numero
    if estado is not None and estado not in ESTADOS:
        raise ValueError("estado inválido")
    try:
        desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date() if fecha_desde else None
        hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date() if fecha_hasta else None
    except ValueError:
        raise ValueError("Las fechas deben tener formato AAAA-MM-DD")
    if desde and hasta and desde > hasta:
        raise ValueError("fecha_desde debe ser menor o igual a fecha_hasta")
    return resultado


def validar_recurrente(datos):
    if not isinstance(datos, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")
    permitidos = {"id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin", "cantidad_semanas"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        raise ValueError(f"Campo(s) desconocido(s): {', '.join(sorted(desconocidos))}")
    faltantes = permitidos - set(datos)
    if faltantes:
        raise ValueError(f"Falta(n) campo(s) obligatorio(s): {', '.join(sorted(faltantes))}")
    cantidad = datos["cantidad_semanas"]
    if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 2 or cantidad > 12:
        raise ValueError("cantidad_semanas debe ser un entero entre 2 y 12")
    base = {campo: datos[campo] for campo in ("id_socio", "id_cancha", "fecha_hora_inicio", "fecha_hora_fin")}
    id_socio, id_cancha, inicio, fin, horas = validar_creacion(base)
    return id_socio, id_cancha, inicio, fin, horas, cantidad
