import mysql.connector
from api_club.config import DB_HOST, DB_USER, DB_PASSWORD, DB_PORT, DB_NAME


def obtener_conexion():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        database=DB_NAME,
    )
