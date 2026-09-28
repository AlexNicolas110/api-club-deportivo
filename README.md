# API de Reservas del Club Deportivo Encuentro

## Integrante:

- Alex Nicolas Benitez Olmedo

## Descripción:

API REST desarrollada con Python, Flask y MySQL para administrar deportes, canchas, socios, disponibilidad y reservas de un club deportivo.

## Herramientas:

- Python 3.12.3
- Flask 3.1.3
- MySQL 8.0.46
- mysql-connector-python
- python-dotenv 1.2.3

## Instalación:

Crear el entorno virtual:

python3 -m venv .venv

Activarlo en Linux:

source .venv/bin/activate

Instalar dependencias:

pip install -r requirements.txt

Copiar ".env.example" como ".env" y completar los datos de MySQL:

env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_clave
DB_PORT=3306
DB_NAME=club_encuentro

Crear la base y las tablas:

mysql -u root -p < db/init_db.sql

Los datos ficticios opcionales se pueden cargar con:

mysql -u root -p < db/datos_prueba.sql

Ejecutar la API:

python app.py

La aplicación queda disponible en "http://127.0.0.1:5000".

## Endpoints:

### Deportes:

- GET /deportes

### Canchas:

- GET /canchas
- POST /canchas
- GET /canchas/{id}
- PATCH /canchas/{id}
- DELETE /canchas/{id}
- GET /canchas/disponibles

### Socios:

- GET /socios
- POST /socios
- GET /socios/{id}
- PATCH /socios/{id}

### Reservas:

- GET /reservas
- POST /reservas
- GET /reservas/{id}
- PUT /reservas/{id}/estado

### Extensiones incluidas en Swagger:

- GET /bloqueos
- POST /bloqueos
- DELETE /bloqueos/{id}
- POST /reservas/recurrentes

## Reglas principales:

Las reservas se interpretan en GMT-3 y usan el formato `YYYY-MM-DDTHH:MM:SS.ffffff-03:00`. Deben comenzar en el futuro, usar horas en punto, durar entre una y tres horas, y quedar completamente dentro del horario de 08:00 a 23:00.

No puede existir una reserva confirmada superpuesta para la misma cancha ni para el mismo socio. Los turnos consecutivos sí están permitidos.

El precio se expresa en centavos. Al crear una reserva se copia el precio vigente de la cancha y se calcula el total. Ese valor queda guardado aunque después cambie la tarifa de la cancha.

Toda reserva se crea como "confirmada". Puede cancelarse antes de su inicio y finalizarse una vez alcanzado su horario de fin. Las reservas canceladas o finalizadas no pueden reactivarse.

Los listados usan "_limit" y "_offset", se ordenan por "id" ascendente y devuelven enlaces HATEOAS. Cuando el Swagger define "204" para un listado sin resultados, la implementación devuelve "204" sin cuerpo.

## Ejemplos:

Crear un socio:

curl -X POST http://127.0.0.1:5000/socios \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana Pérez","email":"ana@example.com"}'

Crear una cancha:

curl -X POST http://127.0.0.1:5000/canchas \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Cancha 1","id_deporte":1,"precio_hora":1000000}'

Consultar disponibilidad:

curl "http://127.0.0.1:5000/canchas/disponibles?fecha=2026-10-15&hora_inicio=18:00:00&hora_fin=20:00:00"

Crear una reserva:

curl -X POST http://127.0.0.1:5000/reservas \
  -H "Content-Type: application/json" \
  -d '{"id_socio":1,"id_cancha":1,"fecha_hora_inicio":"2026-10-15T18:00:00.000000-03:00","fecha_hora_fin":"2026-10-15T20:00:00.000000-03:00"}'

Al probar reservas se debe usar una fecha futura respecto del momento de la prueba.

## Pruebas:

Para las pruebas de integración se usa una base separada llamada "club_encuentro_test".

Crear esa base con:

mysql -u root -p < db/init_test_db.sql

Instalar pytest si no está disponible:

pip install pytest

Ejecutar:

pytest
