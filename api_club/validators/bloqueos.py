from datetime import datetime, timedelta, timezone


TZ = timezone(timedelta(hours=-3))


def validar_creacion(datos):
    if not isinstance(datos, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")
    permitidos = {"id_cancha", "fecha", "hora_inicio", "hora_fin", "motivo"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        raise ValueError(f"Campo(s) desconocido(s): {', '.join(sorted(desconocidos))}")
    faltantes = permitidos - set(datos)
    if faltantes:
        raise ValueError(f"Falta(n) campo(s) obligatorio(s): {', '.join(sorted(faltantes))}")
    id_cancha = datos["id_cancha"]
    motivo = datos["motivo"]
    if not isinstance(id_cancha, int) or isinstance(id_cancha, bool) or id_cancha < 1:
        raise ValueError("id_cancha debe ser un entero positivo")
    if not isinstance(motivo, str) or not motivo.strip():
        raise ValueError("motivo no puede estar vacío")
    try:
        fecha = datetime.strptime(datos["fecha"], "%Y-%m-%d").date()
        inicio = datetime.strptime(datos["hora_inicio"], "%H:%M:%S").time()
        fin = datetime.strptime(datos["hora_fin"], "%H:%M:%S").time()
    except (TypeError, ValueError):
        raise ValueError("fecha u hora con formato inválido")
    if inicio.minute or inicio.second or fin.minute or fin.second:
        raise ValueError("Las horas deben ser en punto")
    if inicio >= fin or inicio.hour < 8 or fin.hour > 23:
        raise ValueError("El bloqueo debe estar entre 08:00 y 23:00 y tener inicio anterior al fin")
    if datetime.combine(fecha, inicio, tzinfo=TZ) <= datetime.now(TZ):
        raise ValueError("El bloqueo debe comenzar en el futuro")
    return id_cancha, fecha, inicio, fin, motivo.strip()
