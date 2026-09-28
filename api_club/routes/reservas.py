from flask import Blueprint, jsonify, request
from api_club.services import reservas as service
from api_club.validators import reservas as validator
from api_club.utils import formatear_error, links_paginacion, parse_id, parse_paginacion, validar_parametros


reservas_bp = Blueprint("reservas", __name__)


def respuesta_error(code, message, description, status):
    return jsonify(formatear_error(code, message, description)), status


@reservas_bp.route("/reservas", methods=["GET"])
def listar_reservas():
    permitidos = {"_limit", "_offset", "id_cancha", "id_socio", "estado", "fecha_desde", "fecha_hasta"}
    error = validar_parametros(request.args, permitidos)
    if error:
        return respuesta_error("ERROR_VALIDACION", "Parámetros inválidos", error, 400)
    try:
        limit, offset = parse_paginacion(request.args)
        filtros = validator.validar_filtros(
            request.args.get("id_cancha"),
            request.args.get("id_socio"),
            request.args.get("estado"),
            request.args.get("fecha_desde"),
            request.args.get("fecha_hasta"),
        )
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Filtros inválidos", str(ex), 400)
    reservas = service.listar_reservas(limit, offset, **filtros)
    if not reservas:
        return "", 204
    total = service.contar_reservas(**filtros)
    return jsonify({"reservas": reservas, "_links": links_paginacion(request, total, limit, offset)}), 200


@reservas_bp.route("/reservas", methods=["POST"])
def crear_reserva():
    try:
        datos = validator.validar_creacion(request.get_json(silent=True))
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Reserva inválida", str(ex), 400)
    _, motivo = service.crear(*datos)
    if motivo in {"SOCIO_NO_EXISTE", "CANCHA_NO_EXISTE"}:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Recurso no encontrado", motivo, 404)
    if motivo:
        return respuesta_error("ERROR_CONFLICTO", "No se puede crear la reserva", motivo, 409)
    return "", 201


@reservas_bp.route("/reservas/<id_reserva>", methods=["GET"])
def obtener_reserva(id_reserva):
    try:
        id_reserva = parse_id(id_reserva)
    except ValueError as ex:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Reserva no encontrada", str(ex), 404)
    reserva = service.obtener(id_reserva)
    if not reserva:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Reserva no encontrada", "No existe una reserva con ese ID", 404)
    return jsonify(reserva), 200


@reservas_bp.route("/reservas/<id_reserva>/estado", methods=["PUT"])
def cambiar_estado(id_reserva):
    try:
        id_reserva = parse_id(id_reserva)
        nuevo_estado = validator.validar_estado(request.get_json(silent=True))
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Solicitud inválida", str(ex), 400)
    motivo = service.cambiar_estado(id_reserva, nuevo_estado)
    if motivo == "NO_EXISTE":
        return respuesta_error("ERROR_NO_ENCONTRADO", "Reserva no encontrada", "No existe una reserva con ese ID", 404)
    if motivo:
        return respuesta_error("ERROR_CONFLICTO", "Transición no permitida", "El cambio de estado no está permitido en este momento", 409)
    return "", 204


@reservas_bp.route("/reservas/recurrentes", methods=["POST"])
def crear_recurrentes():
    try:
        datos = validator.validar_recurrente(request.get_json(silent=True))
    except ValueError as ex:
        return respuesta_error("ERROR_VALIDACION", "Reserva recurrente inválida", str(ex), 400)
    _, motivo, conflictos = service.crear_recurrentes(*datos)
    if motivo in {"SOCIO_NO_EXISTE", "CANCHA_NO_EXISTE"}:
        return respuesta_error("ERROR_NO_ENCONTRADO", "Recurso no encontrado", motivo, 404)
    if motivo:
        cuerpo = formatear_error("ERROR_CONFLICTO", "Serie con conflictos", "Una o más fechas no están disponibles")
        cuerpo["conflictos"] = conflictos
        return jsonify(cuerpo), 409
    return "", 201
