USE club_encuentro;

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
    ('Cancha Fútbol 1', 1, 1000000, FALSE, TRUE),
    ('Cancha Pádel 1', 2, 800000, TRUE, TRUE),
    ('Cancha Tenis 1', 3, 700000, FALSE, TRUE);

INSERT INTO socios (nombre, email, activo) VALUES
    ('Ana Pérez', 'ana@example.com', TRUE),
    ('Bruno García', 'bruno@example.com', TRUE),
    ('Carla López', 'carla@example.com', FALSE);
