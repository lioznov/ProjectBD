CREATE DATABASE IF NOT EXISTS travel_db;
USE travel_db;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user'
);

CREATE TABLE tour (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,
    description TEXT
);

CREATE TABLE review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tour_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL,
    FOREIGN KEY (tour_id) REFERENCES tour(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tour_id INT NOT NULL,
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (tour_id) REFERENCES tour(id)
);

-- Тестовые данные для туров
INSERT INTO tour (name, destination, price, description, country)
VALUES
    ('Пляжный отдых', 'Мальдивы', 1200.00, 'Отдых на белоснежных пляжах.', 'Мальдивы'),
    ('Городское приключение', 'Париж', 900.00, 'Исследуйте город огней.', 'Франция');

-- Тестовые данные для отзывов (предполагая user_id=1 и tour_id=1,2)
INSERT INTO review (tour_id, user_id, rating, comment)
VALUES
    (1, 1, 5, 'Потрясающий отдых! Рекомендую всем!'),
    (2, 1, 4, 'Хороший тур, но дороговато.');