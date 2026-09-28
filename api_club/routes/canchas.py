from flask import Blueprint, jsonify, request
from api_club.services import canchas as service
from api_club.validators import canchas as validator
from api_club.utils import formatear_error, links_paginacion, parse_bool, parse_id, parse_paginacion, validar_parametros


canchas_bp = Blueprint("canchas", __name__)


def respuesta_error(code, message, description, status):
    return jsonify(formatear_error(code, message, description)), status


@canchas_bp.route("/canchas", methods=["GET"])
def listar_canchas():
    error = validar_parametros(request.args, {"_limit", "_offset", "nombre", "id_deporte", "techada", "activa"})
    if error:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", error, 400)
    try:
        limit, offset = parse_paginacion(request.args)
        id_deporte = parse_id(request.args["id_deporte"], "id_deporte") if "id_deporte" in request.args else None
        techada = parse_bool(request.args.get("techada"), "techada")
        activa = parse_bool(request.args.get("activa"), "activa")
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", str(ex), 400)
    nombre = request.args.get("nombre")
    canchas = service.listar_canchas(limit, offset, nombre, id_deporte, techada, activa)
    if not canchas:
        return "", 204
    total = service.contar_canchas(nombre, id_deporte, techada, activa)
    return jsonify({"canchas": canchas, "_links": links_paginacion(request, total, limit, offset)}), 200


@canchas_bp.route("/canchas", methods=["POST"])
def crear_cancha():
    try:
        datos = validator.validar_creacion(request.get_json(silent=True))
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Datos inválidos", str(ex), 400)
    _, motivo = service.crear_cancha(*datos)
    if motivo:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Deporte no encontrado", "El deporte indicado no existe", 404)
    return "", 201


@canchas_bp.route("/canchas/disponibles", methods=["GET"])
def consultar_disponibilidad():
    permitidos = {"fecha", "hora_inicio", "hora_fin", "id_deporte", "techada", "_limit", "_offset"}
    error = validar_parametros(request.args, permitidos)
    if error:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", error, 400)
    try:
        limit, offset = parse_paginacion(request.args)
        id_deporte = parse_id(request.args["id_deporte"], "id_deporte") if "id_deporte" in request.args else None
        techada = parse_bool(request.args.get("techada"), "techada")
        fecha = request.args.get("fecha")
        hora_inicio = request.args.get("hora_inicio")
        hora_fin = request.args.get("hora_fin")
        validator.validar_disponibilidad(fecha, hora_inicio, hora_fin)
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", str(ex), 400)
    canchas = service.consultar_disponibilidad(fecha, hora_inicio, hora_fin, id_deporte, techada, limit, offset)
    if not canchas:
        return "", 204
    total = service.contar_disponibles(fecha, hora_inicio, hora_fin, id_deporte, techada)
    return jsonify({"canchas": canchas, "_links": links_paginacion(request, total, limit, offset)}), 200


@canchas_bp.route("/canchas/<id_cancha>", methods=["GET"])
def obtener_cancha(id_cancha):
    try:
        id_cancha = parse_id(id_cancha)
    except ValueError as ex:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Cancha no encontrada", str(ex), 404)
    cancha = service.obtener_cancha_por_id(id_cancha)
    if not cancha:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Cancha no encontrada", "No existe una cancha con ese ID", 404)
    return jsonify(cancha), 200


@canchas_bp.route("/canchas/<id_cancha>", methods=["PATCH"])
def actualizar_cancha(id_cancha):
    try:
        id_cancha = parse_id(id_cancha)
        datos = validator.validar_actualizacion(request.get_json(silent=True))
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Datos inválidos", str(ex), 400)
    if not service.actualizar_cancha(id_cancha, datos):
        return respuesta_error("ERROR_NO_ENCONTRADO", "Cancha no encontrada", "No existe una cancha con ese ID", 404)
    return "", 204


@canchas_bp.route("/canchas/<id_cancha>", methods=["DELETE"])
def eliminar_cancha(id_cancha):
    try:
        id_cancha = parse_id(id_cancha)
    except ValueError as ex:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Cancha no encontrada", str(ex), 404)
    eliminada, motivo = service.eliminar_cancha(id_cancha)
    if motivo == "NO_ENCONTRADA":
        return respuesta_error("ERROR_NO_ENCONTRADO", "Cancha no encontrada", "No existe una cancha con ese ID", 404)
    if motivo == "TIENE_RESERVAS":
        return respuesta_error("ERROR_CONFLICTO", "No se puede eliminar la cancha", "La cancha tiene reservas asociadas", 409)
    return "", 204
