from datetime import datetime, timedelta, timezone


TZ = timezone(timedelta(hours=-3))


def validar_creacion(datos):
    if not isinstance(datos, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")
    permitidos = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        raise ValueError(f"Campo(s) desconocido(s): {', '.join(sorted(desconocidos))}")
    obligatorios = {"nombre", "id_deporte", "precio_hora"}
    faltantes = obligatorios - set(datos)
    if faltantes:
        raise ValueError(f"Falta(n) campo(s) obligatorio(s): {', '.join(sorted(faltantes))}")
    nombre = datos["nombre"]
    id_deporte = datos["id_deporte"]
    precio_hora = datos["precio_hora"]
    techada = datos.get("techada", False)
    activa = datos.get("activa", True)
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("nombre no puede estar vacío")
    if not isinstance(id_deporte, int) or isinstance(id_deporte, bool) or id_deporte < 1:
        raise ValueError("id_deporte debe ser un entero positivo")
    if not isinstance(precio_hora, int) or isinstance(precio_hora, bool) or precio_hora <= 0:
        raise ValueError("precio_hora debe ser un entero positivo")
    if not isinstance(techada, bool):
        raise ValueError("techada debe ser true o false")
    if not isinstance(activa, bool):
        raise ValueError("activa debe ser true o false")
    return nombre.strip(), id_deporte, precio_hora, techada, activa


def validar_actualizacion(datos):
    if not isinstance(datos, dict) or not datos:
        raise ValueError("El cuerpo debe ser un objeto JSON no vacío")
    permitidos = {"nombre", "precio_hora", "techada", "activa"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        raise ValueError(f"Campo(s) desconocido(s): {', '.join(sorted(desconocidos))}")
    resultado = {}
    if "nombre" in datos:
        if not isinstance(datos["nombre"], str) or not datos["nombre"].strip():
            raise ValueError("nombre no puede estar vacío")
        resultado["nombre"] = datos["nombre"].strip()
    if "precio_hora" in datos:
        valor = datos["precio_hora"]
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ValueError("precio_hora debe ser un entero positivo")
        resultado["precio_hora"] = valor
    for campo in ("techada", "activa"):
        if campo in datos:
            if not isinstance(datos[campo], bool):
                raise ValueError(f"{campo} debe ser true o false")
            resultado[campo] = datos[campo]
    return resultado


def validar_disponibilidad(fecha, hora_inicio, hora_fin):
    if not fecha or not hora_inicio or not hora_fin:
        raise ValueError("fecha, hora_inicio y hora_fin son obligatorios")
    try:
        dia = datetime.strptime(fecha, "%Y-%m-%d").date()
        inicio = datetime.strptime(hora_inicio, "%H:%M:%S").time()
        fin = datetime.strptime(hora_fin, "%H:%M:%S").time()
    except ValueError:
        raise ValueError("fecha u hora con formato inválido")
    if inicio.minute or inicio.second or fin.minute or fin.second:
        raise ValueError("hora_inicio y hora_fin deben ser horas en punto")
    if inicio >= fin:
        raise ValueError("hora_inicio debe ser menor que hora_fin")
    if inicio.hour < 8 or fin.hour > 23:
        raise ValueError("El intervalo debe estar entre 08:00 y 23:00")
    inicio_completo = datetime.combine(dia, inicio, tzinfo=TZ)
    fin_completo = datetime.combine(dia, fin, tzinfo=TZ)
    horas = int((fin_completo - inicio_completo).total_seconds() / 3600)
    if horas < 1 or horas > 3:
        raise ValueError("El intervalo debe durar entre 1 y 3 horas completas")
    if inicio_completo <= datetime.now(TZ):
        raise ValueError("El intervalo debe comenzar en el futuro")
