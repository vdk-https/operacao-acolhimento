CREATE DATABASE IF NOT EXISTS acolhimento_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE acolhimento_db;

CREATE TABLE IF NOT EXISTS registros (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    grupo VARCHAR(80) NOT NULL,
    necessidade VARCHAR(120) NOT NULL,
    observacao VARCHAR(400) NOT NULL,
    prioridade ENUM('baixo', 'medio', 'alto') NOT NULL,
    situacao ENUM('aberto', 'resolvido') NOT NULL DEFAULT 'aberto',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_grupo (grupo),
    INDEX idx_situacao (situacao)
) ENGINE=InnoDB;

