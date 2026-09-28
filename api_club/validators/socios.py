import re


PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_creacion(datos):
    if not isinstance(datos, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")
    permitidos = {"nombre", "email"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        raise ValueError(f"Campo(s) desconocido(s): {', '.join(sorted(desconocidos))}")
    faltantes = permitidos - set(datos)
    if faltantes:
        raise ValueError(f"Falta(n) campo(s) obligatorio(s): {', '.join(sorted(faltantes))}")
    nombre = datos["nombre"]
    email = datos["email"]
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("nombre no puede estar vacío")
    if not isinstance(email, str) or not PATRON_EMAIL.fullmatch(email.strip()):
        raise ValueError("email no tiene un formato válido")
    return {"nombre": nombre.strip(), "email": email.strip().lower()}


def validar_actualizacion(datos):
    if not isinstance(datos, dict) or not datos:
        raise ValueError("El cuerpo debe ser un objeto JSON no vacío")
    permitidos = {"nombre", "email", "activo"}
    desconocidos = set(datos) - permitidos
    if desconocidos:
        raise ValueError(f"Campo(s) desconocido(s): {', '.join(sorted(desconocidos))}")
    resultado = {}
    if "nombre" in datos:
        if not isinstance(datos["nombre"], str) or not datos["nombre"].strip():
            raise ValueError("nombre no puede estar vacío")
        resultado["nombre"] = datos["nombre"].strip()
    if "email" in datos:
        email = datos["email"]
        if not isinstance(email, str) or not PATRON_EMAIL.fullmatch(email.strip()):
            raise ValueError("email no tiene un formato válido")
        resultado["email"] = email.strip().lower()
    if "activo" in datos:
        if not isinstance(datos["activo"], bool):
            raise ValueError("activo debe ser true o false")
        resultado["activo"] = datos["activo"]
    return resultado

validar_alta_socio = validar_creacion
validar_actualizacion_socio = validar_actualizacion
