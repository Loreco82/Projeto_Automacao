# =====================================================================
# core/importador_excel.py
# Le as consultas a partir de uma planilha Excel e grava no banco.
#
# A planilha deve ter as colunas (na primeira linha, como cabecalho):
#   paciente | email | telefone | medico | especialidade | data_hora | local
#
# A coluna data_hora deve estar no formato:  AAAA-MM-DD HH:MM
#   exemplo: 2026-06-15 14:30
# =====================================================================

import openpyxl

from config import CAMINHO_EXCEL
from database import db_manager
from utils.logger import obter_logger

logger = obter_logger()

# Colunas obrigatorias que a planilha precisa ter.
COLUNAS_ESPERADAS = [
    "paciente", "email", "telefone",
    "medico", "especialidade", "data_hora", "local",
]


def importar_consultas(caminho=CAMINHO_EXCEL):
    """Le o Excel e insere pacientes e consultas no banco.

    Retorna a quantidade de consultas novas que foram importadas.
    Consultas que ja existiam (mesmo paciente + mesmo horario) sao
    ignoradas, evitando duplicidade.
    """
    logger.info("Iniciando importacao da planilha: %s", caminho)

    # data_only=True faz o openpyxl ler o valor calculado das celulas
    # (e nao a formula), o que e o que precisamos aqui.
    planilha = openpyxl.load_workbook(caminho, data_only=True)
    aba = planilha.active

    # Le o cabecalho (primeira linha) e monta um mapa nome_coluna -> indice.
    cabecalho = [str(c.value).strip().lower() if c.value else "" for c in aba[1]]
    indices = {nome: cabecalho.index(nome) for nome in COLUNAS_ESPERADAS
               if nome in cabecalho}

    # Valida se todas as colunas obrigatorias estao presentes.
    faltando = [c for c in COLUNAS_ESPERADAS if c not in indices]
    if faltando:
        raise ValueError(
            "A planilha esta sem as colunas obrigatorias: " + ", ".join(faltando)
        )

    novas = 0

    # itera a partir da linha 2 (a linha 1 e o cabecalho).
    for numero_linha, linha in enumerate(aba.iter_rows(min_row=2, values_only=True), start=2):
        # Pula linhas totalmente vazias.
        if linha is None or all(valor is None for valor in linha):
            continue

        try:
            paciente = str(linha[indices["paciente"]]).strip()
            email = str(linha[indices["email"]]).strip()
            telefone = str(linha[indices["telefone"]]).strip()
            medico = str(linha[indices["medico"]]).strip()
            especialidade = str(linha[indices["especialidade"]]).strip()
            data_hora = _normalizar_data(linha[indices["data_hora"]])
            local = str(linha[indices["local"]]).strip()

            # Cria/recupera o paciente e insere a consulta (se for nova).
            paciente_id = db_manager.obter_ou_criar_paciente(paciente, email, telefone)

            if db_manager.consulta_ja_existe(paciente_id, data_hora):
                logger.info("Linha %s ignorada (consulta ja cadastrada).", numero_linha)
                continue

            db_manager.inserir_consulta(paciente_id, medico, especialidade, data_hora, local)
            novas += 1
            logger.info("Consulta importada: %s em %s.", paciente, data_hora)

        except Exception as erro:
            # Um erro em uma linha nao deve derrubar a importacao inteira.
            logger.error("Erro ao importar a linha %s: %s", numero_linha, erro)

    logger.info("Importacao concluida. %s nova(s) consulta(s).", novas)
    return novas


def _normalizar_data(valor):
    """Converte a data lida da planilha para o texto 'AAAA-MM-DD HH:MM'.

    O openpyxl pode devolver a data como objeto datetime (quando a celula
    esta formatada como data) ou como texto. Tratamos os dois casos.
    """
    from datetime import datetime

    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M")

    # Se vier como texto, tenta interpretar nos formatos mais comuns.
    texto = str(valor).strip()
    for formato in ("%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue

    raise ValueError(f"Formato de data invalido: '{texto}'")
