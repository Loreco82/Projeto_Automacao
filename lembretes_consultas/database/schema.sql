-- =====================================================================
-- schema.sql
-- Script de criação das tabelas do banco de dados SQLite.
-- Sistema Automatizado de Lembretes de Consultas (E-mail e WhatsApp).
--
-- Para rodar manualmente:
--   sqlite3 lembretes.db < database/schema.sql
-- =====================================================================

-- Habilita verificação de chaves estrangeiras (desligada por padrão no SQLite).
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Tabela: pacientes
-- Guarda os dados de contato de cada paciente.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pacientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,  -- identificador único
    nome      TEXT    NOT NULL,                    -- nome completo
    email     TEXT,                                -- e-mail de contato
    telefone  TEXT,                                -- telefone no formato +55DDDNUMERO
    criado_em TEXT    DEFAULT CURRENT_TIMESTAMP     -- data de cadastro
);

-- ---------------------------------------------------------------------
-- Tabela: consultas
-- Cada linha representa um agendamento de consulta.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS consultas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id   INTEGER NOT NULL,                 -- FK -> pacientes.id
    medico        TEXT,                             -- nome do profissional
    especialidade TEXT,                             -- ex.: Cardiologia
    data_hora     TEXT    NOT NULL,                 -- data/hora no padrão ISO (YYYY-MM-DD HH:MM)
    local         TEXT,                             -- endereço/sala da consulta
    status        TEXT    DEFAULT 'agendada',       -- agendada | realizada | cancelada
    criado_em     TEXT    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- ---------------------------------------------------------------------
-- Tabela: historico_envios
-- Registra cada lembrete enviado. A restrição UNIQUE é o mecanismo
-- central de controle: impede que o mesmo lembrete (mesma consulta,
-- mesmo tipo e mesmo canal) seja enviado mais de uma vez.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS historico_envios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    consulta_id   INTEGER NOT NULL,                 -- FK -> consultas.id
    tipo_lembrete TEXT    NOT NULL,                 -- '7d' | '24h' | '3h'
    canal         TEXT    NOT NULL,                 -- 'email' | 'whatsapp'
    status        TEXT    NOT NULL,                 -- 'sucesso' | 'falha'
    detalhe       TEXT,                             -- mensagem de erro ou id do provedor
    enviado_em    TEXT    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consulta_id) REFERENCES consultas(id),
    UNIQUE (consulta_id, tipo_lembrete, canal)      -- evita envio duplicado
);

-- Índices para acelerar as consultas mais frequentes do sistema.
CREATE INDEX IF NOT EXISTS idx_consultas_data ON consultas (data_hora);
CREATE INDEX IF NOT EXISTS idx_envios_consulta ON historico_envios (consulta_id);
