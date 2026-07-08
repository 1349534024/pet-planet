-- MySQL initialization for Pet Planet.
-- Run with a privileged MySQL account before executing Alembic migrations.

CREATE DATABASE IF NOT EXISTS `pet_planet`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

ALTER DATABASE `pet_planet`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'pet'@'%' IDENTIFIED BY 'pet123456';
CREATE USER IF NOT EXISTS 'pet'@'localhost' IDENTIFIED BY 'pet123456';
CREATE USER IF NOT EXISTS 'pet'@'127.0.0.1' IDENTIFIED BY 'pet123456';

ALTER USER 'pet'@'%' IDENTIFIED BY 'pet123456';
ALTER USER 'pet'@'localhost' IDENTIFIED BY 'pet123456';
ALTER USER 'pet'@'127.0.0.1' IDENTIFIED BY 'pet123456';

GRANT ALL PRIVILEGES ON `pet_planet`.* TO 'pet'@'%';
GRANT ALL PRIVILEGES ON `pet_planet`.* TO 'pet'@'localhost';
GRANT ALL PRIVILEGES ON `pet_planet`.* TO 'pet'@'127.0.0.1';

FLUSH PRIVILEGES;
