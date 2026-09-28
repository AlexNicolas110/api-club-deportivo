from datetime import datetime
from urllib.parse import urlencode


def formatear_error(code, message, description, level="error"):
    return {
        "errors": [
            {
                "code": code,
                "message": message,
                "level": level,
                "description": description,
            }
        ]
    }


def validar_parametros(args, permitidos):
    desconocidos = set(args.keys()) - set(permitidos)
    if desconocidos:
        return f"Parámetro(s) desconocido(s): {', '.join(sorted(desconocidos))}"
    return None


def parse_bool(valor, nombre):
    if valor is None:
        return None
    if valor == "true":
        return True
    if valor == "false":
        return False
    raise ValueError(f"{nombre} debe ser true o false")


def parse_id(valor, nombre="id"):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} debe ser un número entero")
    if numero < 1:
        raise ValueError(f"{nombre} debe ser un número positivo")
    return numero


def parse_paginacion(args):
    try:
        limit = int(args.get("_limit", 10))
        offset = int(args.get("_offset", 0))
    except (TypeError, ValueError):
        raise ValueError("_limit y _offset deben ser números enteros")
    if limit < 1 or limit > 100:
        raise ValueError("_limit debe estar entre 1 y 100")
    if offset < 0:
        raise ValueError("_offset no puede ser negativo")
    return limit, offset


def links_paginacion(request, total, limit, offset):
    ultimo = ((total - 1) // limit) * limit if total else 0
    anterior = offset - limit if offset >= limit else None
    siguiente = offset + limit if offset + limit < total else None

    def crear_link(nuevo_offset):
        parametros = request.args.to_dict()
        parametros["_limit"] = limit
        parametros["_offset"] = nuevo_offset
        return {"href": f"{request.base_url}?{urlencode(parametros)}"}

    return {
        "_first": crear_link(0),
        "_prev": crear_link(anterior) if anterior is not None else None,
        "_next": crear_link(siguiente) if siguiente is not None else None,
        "_last": crear_link(ultimo),
    }


def fecha_hora_api(valor):
    if isinstance(valor, str):
        valor = datetime.fromisoformat(valor)
    return valor.strftime("%Y-%m-%dT%H:%M:%S.%f-03:00")
