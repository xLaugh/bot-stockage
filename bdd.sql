CREATE DATABASE IF NOT EXISTS vagos;

USE vagos;

CREATE TABLE IF NOT EXISTS items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS coffre (
    item_name VARCHAR(255) PRIMARY KEY,
    quantity INT NOT NULL DEFAULT 0
);