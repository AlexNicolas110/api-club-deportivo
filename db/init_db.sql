CREATE DATABASE IF NOT EXISTS club_encuentro;
USE club_encuentro;

CREATE TABLE IF NOT EXISTS deportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(190) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS canchas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(190) NOT NULL,
    id_deporte INT NOT NULL,
    precio_hora INT NOT NULL CHECK (precio_hora > 0),
    techada BOOLEAN NOT NULL DEFAULT FALSE,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_deporte) REFERENCES deportes(id)
);

CREATE TABLE IF NOT EXISTS socios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(190) NOT NULL,
    email VARCHAR(190) NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_socio INT NOT NULL,
    id_cancha INT NOT NULL,
    fecha_hora_inicio DATETIME NOT NULL,
    fecha_hora_fin DATETIME NOT NULL,
    precio_hora INT NOT NULL CHECK (precio_hora > 0),
    precio_total INT NOT NULL CHECK (precio_total > 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'confirmada' CHECK (estado IN ('confirmada', 'cancelada', 'finalizada')),
    FOREIGN KEY (id_socio) REFERENCES socios(id),
    FOREIGN KEY (id_cancha) REFERENCES canchas(id)
);

CREATE TABLE IF NOT EXISTS bloqueos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cancha INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_cancha) REFERENCES canchas(id)
);

INSERT IGNORE INTO deportes (id, nombre) VALUES
    (1, 'Fútbol'),
    (2, 'Pádel'),
    (3, 'Tenis');
