from api_club.repositories import bloqueos as repo


def listar(limit, offset, id_cancha=None, fecha=None):
    return repo.listar(limit, offset, id_cancha, fecha)


def contar(id_cancha=None, fecha=None):
    return repo.contar(id_cancha, fecha)


def crear(id_cancha, fecha, inicio, fin, motivo):
    return repo.crear(id_cancha, fecha, inicio, fin, motivo)


def eliminar(id_bloqueo):
    return repo.eliminar(id_bloqueo)
