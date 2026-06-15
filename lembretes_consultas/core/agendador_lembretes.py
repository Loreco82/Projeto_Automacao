# =====================================================================
# core/agendador_lembretes.py
# Cerebro do sistema: decide QUAIS lembretes precisam ser enviados AGORA.
#
# Para cada consulta futura, calcula quanto tempo falta e verifica se
# esse intervalo cai dentro de alguma das janelas configuradas
# (7 dias, 24 horas ou 3 horas). Se cair e o lembrete ainda nao tiver
# sido enviado, dispara e-mail e WhatsApp.
# =====================================================================

from datetime import datetime

from config import REGRAS_LEMBRETES, DESCRICAO_LEMBRETE
from database import db_manager
from core.enviador_email import enviar_email
from core.enviador_whatsapp import enviar_whatsapp
from utils.logger import obter_logger

logger = obter_logger()


def _tipo_de_lembrete_devido(data_consulta, agora):
    """Descobre qual lembrete (se algum) deve ser enviado neste momento.

    Compara as horas que faltam para a consulta com cada regra. A
    'tolerancia' cria uma janela ao redor do horario-alvo: por exemplo,
    o lembrete de 24h e disparado quando faltam entre 22h e 26h.

    Retorna o codigo do lembrete ('7d', '24h', '3h') ou None.
    """
    horas_restantes = (data_consulta - agora).total_seconds() / 3600

    # Ignora consultas que ja passaram.
    if horas_restantes < 0:
        return None

    for codigo, antecedencia, tolerancia in REGRAS_LEMBRETES:
        # A consulta esta dentro da janela [antecedencia - tol, antecedencia + tol]?
        if (antecedencia - tolerancia) <= horas_restantes <= (antecedencia + tolerancia):
            return codigo

    return None


def _enviar_por_canal(consulta, tipo, canal, funcao_envio, descricao):
    """Envia um lembrete por UM canal, respeitando o controle de duplicidade."""
    consulta_id = consulta["consulta_id"]

    # 1o nivel de protecao: ja foi enviado com sucesso? entao nao repete.
    if db_manager.lembrete_ja_enviado(consulta_id, tipo, canal):
        logger.info("Lembrete %s/%s da consulta %s ja enviado. Pulando.",
                    tipo, canal, consulta_id)
        return

    # Tenta enviar e registra o resultado (sucesso ou falha) no historico.
    sucesso, detalhe = funcao_envio(consulta, descricao)
    status = "sucesso" if sucesso else "falha"
    db_manager.registrar_envio(consulta_id, tipo, canal, status, detalhe)


def processar_lembretes():
    """Funcao principal do modulo: percorre as consultas e envia o que for devido.

    Retorna a quantidade de lembretes efetivamente processados.
    """
    agora = datetime.now()
    consultas = db_manager.listar_consultas_futuras()
    logger.info("Verificando %s consulta(s) futura(s)...", len(consultas))

    processados = 0

    for consulta in consultas:
        data_consulta = datetime.strptime(consulta["data_hora"], "%Y-%m-%d %H:%M")
        tipo = _tipo_de_lembrete_devido(data_consulta, agora)

        if tipo is None:
            continue  # nenhuma janela de lembrete bate com esta consulta agora

        descricao = DESCRICAO_LEMBRETE[tipo]
        logger.info("Consulta %s: enviando lembrete '%s'.",
                    consulta["consulta_id"], tipo)

        # Dispara nos dois canais. Cada um e independente.
        _enviar_por_canal(consulta, tipo, "email", enviar_email, descricao)
        _enviar_por_canal(consulta, tipo, "whatsapp", enviar_whatsapp, descricao)
        processados += 1

    logger.info("Processamento concluido. %s lembrete(s) tratado(s).", processados)
    return processados
