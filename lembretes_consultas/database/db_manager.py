# =====================================================================
# database/db_manager.py
# Camada de acesso ao banco de dados (DAO - Data Access Object).
#
# Toda comunicacao com o SQLite passa por aqui. Isso mantem o resto do
# sistema "limpo": os outros modulos chamam funcoes como
# inserir_consulta() sem precisar saber escrever SQL.
# =====================================================================

import sqlite3

from config import CAMINHO_BANCO, CAMINHO_SCHEMA
from utils.logger import obter_logger

logger = obter_logger()


def conectar():
    """Abre uma conexao com o banco SQLite.

    row_factory = sqlite3.Row faz com que cada linha retornada possa ser
    acessada pelo nome da coluna (ex.: linha["nome"]), o que deixa o
    codigo mais legivel do que usar indices numericos.
    """
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    # Ativa a verificacao de chaves estrangeiras nesta conexao.
    conexao.execute("PRAGMA foreign_keys = ON;")
    return conexao


def inicializar_banco():
    """Cria as tabelas executando o script schema.sql.

    Usa 'IF NOT EXISTS' (dentro do .sql), entao pode ser chamada quantas
    vezes for preciso sem apagar dados existentes.
    """
    with open(CAMINHO_SCHEMA, "r", encoding="utf-8") as arquivo:
        script_sql = arquivo.read()

    with conectar() as conexao:
        conexao.executescript(script_sql)
    logger.info("Banco de dados inicializado (tabelas verificadas/criadas).")


def obter_ou_criar_paciente(nome, email, telefone):
    """Retorna o id de um paciente. Se ele ainda nao existir, cria.

    A identificacao usa o e-mail como chave logica (poderia ser CPF).
    """
    with conectar() as conexao:
        cursor = conexao.execute(
            "SELECT id FROM pacientes WHERE email = ?", (email,)
        )
        linha = cursor.fetchone()
        if linha:
            return linha["id"]

        cursor = conexao.execute(
            "INSERT INTO pacientes (nome, email, telefone) VALUES (?, ?, ?)",
            (nome, email, telefone),
        )
        return cursor.lastrowid


def consulta_ja_existe(paciente_id, data_hora):
    """Verifica se ja existe uma consulta igual (mesmo paciente e horario).

    Evita duplicar consultas a cada vez que a planilha for importada.
    """
    with conectar() as conexao:
        cursor = conexao.execute(
            "SELECT id FROM consultas WHERE paciente_id = ? AND data_hora = ?",
            (paciente_id, data_hora),
        )
        linha = cursor.fetchone()
        return linha["id"] if linha else None


def inserir_consulta(paciente_id, medico, especialidade, data_hora, local):
    """Insere uma nova consulta e devolve o id gerado."""
    with conectar() as conexao:
        cursor = conexao.execute(
            """INSERT INTO consultas
                   (paciente_id, medico, especialidade, data_hora, local)
               VALUES (?, ?, ?, ?, ?)""",
            (paciente_id, medico, especialidade, data_hora, local),
        )
        return cursor.lastrowid


def listar_consultas_futuras():
    """Retorna todas as consultas agendadas que ainda vao acontecer.

    Faz um JOIN com pacientes para ja trazer nome, e-mail e telefone,
    que sao necessarios para montar e enviar os lembretes.
    """
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            SELECT c.id            AS consulta_id,
                   c.medico        AS medico,
                   c.especialidade AS especialidade,
                   c.data_hora     AS data_hora,
                   c.local         AS local,
                   p.nome          AS paciente,
                   p.email         AS email,
                   p.telefone      AS telefone
            FROM consultas c
            JOIN pacientes p ON p.id = c.paciente_id
            WHERE c.status = 'agendada'
              AND datetime(c.data_hora) >= datetime('now', 'localtime')
            ORDER BY c.data_hora
            """
        )
        return cursor.fetchall()


def lembrete_ja_enviado(consulta_id, tipo_lembrete, canal):
    """Consulta se um lembrete especifico ja foi enviado com sucesso.

    Este e o segundo nivel de protecao contra envios duplicados
    (o primeiro e a restricao UNIQUE no banco).
    """
    with conectar() as conexao:
        cursor = conexao.execute(
            """SELECT id FROM historico_envios
               WHERE consulta_id = ? AND tipo_lembrete = ? AND canal = ?
                 AND status = 'sucesso'""",
            (consulta_id, tipo_lembrete, canal),
        )
        return cursor.fetchone() is not None


def registrar_envio(consulta_id, tipo_lembrete, canal, status, detalhe=""):
    """Grava o resultado de um envio no historico.

    Usa INSERT OR REPLACE para conviver com a restricao UNIQUE: se um
    envio que falhou for tentado de novo e der certo, o registro e
    atualizado em vez de gerar erro.
    """
    with conectar() as conexao:
        conexao.execute(
            """INSERT OR REPLACE INTO historico_envios
                   (consulta_id, tipo_lembrete, canal, status, detalhe)
               VALUES (?, ?, ?, ?, ?)""",
            (consulta_id, tipo_lembrete, canal, status, detalhe),
        )
