from api_club.repositories import deportes as deportes_repo


def listar_deportes():
    return deportes_repo.obtener_todos()
