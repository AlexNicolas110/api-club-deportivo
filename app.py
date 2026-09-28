from flask import Flask, jsonify
from api_club.routes.deportes import deportes_bp
from api_club.routes.canchas import canchas_bp
from api_club.routes.socios import socios_bp
from api_club.routes.reservas import reservas_bp
from api_club.routes.bloqueos import bloqueos_bp
from api_club.utils import formatear_error


app = Flask(__name__)
app.register_blueprint(deportes_bp)
app.register_blueprint(canchas_bp)
app.register_blueprint(socios_bp)
app.register_blueprint(reservas_bp)
app.register_blueprint(bloqueos_bp)


@app.errorhandler(500)
def error_interno(_):
    return jsonify(formatear_error("ERROR_INTERNO", "Error interno del servidor", "Ocurrió un error inesperado")), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
