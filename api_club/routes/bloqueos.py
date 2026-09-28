from datetime import datetime
from flask import Blueprint, jsonify, request
from api_club.services import bloqueos as service
from api_club.validators import bloqueos as validator
from api_club.utils import formatear_error, links_paginacion, parse_id, parse_paginacion, validar_parametros


bloqueos_bp = Blueprint("bloqueos", __name__)


def respuesta_error(code, message, description, status):
    return jsonify(formatear_error(code, message, description)), status


@bloqueos_bp.route("/bloqueos", methods=["GET"])
def listar_bloqueos():
    error = validar_parametros(request.args, {"id_cancha", "fecha", "_limit", "_offset"})
    if error:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", error, 400)
    try:
        limit, offset = parse_paginacion(request.args)
        id_cancha = parse_id(request.args["id_cancha"], "id_cancha") if "id_cancha" in request.args else None
        fecha = request.args.get("fecha")
        if fecha:
            datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", str(ex), 400)
    bloqueos = service.listar(limit, offset, id_cancha, fecha)
    if not bloqueos:
        return "", 204
    total = service.contar(id_cancha, fecha)
    return jsonify({"bloqueos": bloqueos, "_links": links_paginacion(request, total, limit, offset)}), 200


@bloqueos_bp.route("/bloqueos", methods=["POST"])
def crear_bloqueo():
    try:
        datos = validator.validar_creacion(request.get_json(silent=True))
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Bloqueo inválido", str(ex), 400)
    _, motivo = service.crear(*datos)
    if motivo == "CANCHA_NO_EXISTE":
        return respuesta_error("ERROR_NO_ENCONTRADO", "Cancha no encontrada", "No existe la cancha", 404)
    if motivo:
        return respuesta_error("ERROR_CONFLICTO", "No se puede crear el bloqueo", motivo, 409)
    return "", 201


@bloqueos_bp.route("/bloqueos/<id_bloqueo>", methods=["DELETE"])
def eliminar_bloqueo(id_bloqueo):
    try:
        id_bloqueo = parse_id(id_bloqueo)
    except ValueError as ex:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Bloqueo no encontrado", str(ex), 404)
    if not service.eliminar(id_bloqueo):
        return respuesta_error("ERROR_NO_ENCONTRADO", "Bloqueo no encontrado", "No existe el bloqueo", 404)
    return "", 204
