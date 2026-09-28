from flask import Blueprint, jsonify, request
from api_club.services import socios as service
from api_club.validators import socios as validator
from api_club.utils import formatear_error, links_paginacion, parse_bool, parse_id, parse_paginacion, validar_parametros


socios_bp = Blueprint("socios", __name__)


def respuesta_error(code, message, description, status):
    return jsonify(formatear_error(code, message, description)), status


@socios_bp.route("/socios", methods=["GET"])
def listar_socios():
    error = validar_parametros(request.args, {"_limit", "_offset", "nombre", "activo"})
    if error:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", error, 400)
    try:
        limit, offset = parse_paginacion(request.args)
        activo = parse_bool(request.args.get("activo"), "activo")
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", str(ex), 400)
    nombre = request.args.get("nombre")
    socios, total = service.get_socios(limit, offset, nombre, activo)
    if not socios:
        return "", 204
    return jsonify({"socios": socios, "_links": links_paginacion(request, total, limit, offset)}), 200


@socios_bp.route("/socios", methods=["POST"])
def crear_socio():
    try:
        datos = validator.validar_creacion(request.get_json(silent=True))
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Datos inválidos", str(ex), 400)
    _, motivo = service.crear_socio(datos["nombre"], datos["email"])
    if motivo == "EMAIL_DUPLICADO":
        return respuesta_error("ERROR_CONFLICTO", "Email duplicado", "Ya existe un socio registrado con ese email", 409)
    return "", 201


@socios_bp.route("/socios/<id_socio>", methods=["GET"])
def obtener_socio(id_socio):
    try:
        id_socio = parse_id(id_socio)
    except ValueError as ex:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Socio no encontrado", str(ex), 404)
    socio = service.obtener_socio_por_id(id_socio)
    if not socio:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Socio no encontrado", "No existe un socio con ese ID", 404)
    return jsonify(socio), 200


@socios_bp.route("/socios/<id_socio>", methods=["PATCH"])
def actualizar_socio(id_socio):
    try:
        id_socio = parse_id(id_socio)
        datos = validator.validar_actualizacion(request.get_json(silent=True))
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Datos inválidos", str(ex), 400)
    _, motivo = service.actualizar_socio(id_socio, datos)
    if motivo == "NO_ENCONTRADO":
        return respuesta_error("ERROR_NO_ENCONTRADO", "Socio no encontrado", "No existe un socio con ese ID", 404)
    if motivo == "EMAIL_DUPLICADO":
        return respuesta_error("ERROR_CONFLICTO", "Email duplicado", "Ya existe un socio registrado con ese email", 409)
    return "", 204
