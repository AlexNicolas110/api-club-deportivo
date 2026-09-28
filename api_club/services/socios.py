from api_club.repositories import socios as repo


def get_socios(limit, offset, nombre=None, activo=None):
    return repo.get_socios(limit, offset, nombre, activo), repo.contar_socios(nombre, activo)


def crear_socio(nombre, email):
    if repo.existe_email(email):
        return None, "EMAIL_DUPLICADO"
    id_nuevo = repo.crear_socio(nombre, email)
    return repo.obtener_por_id(id_nuevo), None


def obtener_socio_por_id(id_socio):
    return repo.obtener_por_id(id_socio)


def actualizar_socio(id_socio, campos):
    if not repo.obtener_por_id(id_socio):
        return None, "NO_ENCONTRADO"
    if "email" in campos and repo.existe_email(campos["email"], id_socio):
        return None, "EMAIL_DUPLICADO"
    repo.actualizar_socio(id_socio, campos)
    return repo.obtener_por_id(id_socio), None
