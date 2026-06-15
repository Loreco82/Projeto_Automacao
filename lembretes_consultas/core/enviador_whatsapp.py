# =====================================================================
# core/enviador_whatsapp.py
# Responsavel por enviar os lembretes via WhatsApp usando a API da Twilio.
#
# A Twilio foi escolhida por oferecer um "sandbox" gratuito do WhatsApp,
# ideal para testes academicos. A mesma logica vale para a WhatsApp
# Business API oficial, mudando apenas a forma de autenticacao.
# =====================================================================

from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM,
    MODO_SIMULACAO,
)
from utils.logger import obter_logger

logger = obter_logger()


def montar_mensagem(consulta, descricao_lembrete):
    """Monta o texto curto da mensagem de WhatsApp."""
    return (
        f"Ola, {consulta['paciente']}! Lembrete de consulta ({descricao_lembrete}).\n"
        f"{consulta['especialidade']} com {consulta['medico']}\n"
        f"Quando: {consulta['data_hora']}\n"
        f"Local: {consulta['local']}"
    )


def enviar_whatsapp(consulta, descricao_lembrete):
    """Envia uma mensagem de WhatsApp de lembrete.

    Retorna (sucesso: bool, detalhe: str). Em MODO_SIMULACAO, apenas
    registra no log, sem chamar a API.
    """
    telefone = consulta["telefone"]
    corpo = montar_mensagem(consulta, descricao_lembrete)

    if MODO_SIMULACAO:
        logger.info("[SIMULACAO] WhatsApp para %s | %s", telefone, descricao_lembrete)
        return True, "simulado"

    try:
        # A importacao fica dentro da funcao para que o sistema rode em
        # modo simulacao mesmo sem a biblioteca 'twilio' instalada.
        from twilio.rest import Client

        cliente = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        mensagem = cliente.messages.create(
            body=corpo,
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{telefone}",
        )

        logger.info("WhatsApp enviado para %s (SID %s).", telefone, mensagem.sid)
        return True, mensagem.sid

    except Exception as erro:
        logger.error("Falha ao enviar WhatsApp para %s: %s", telefone, erro)
        return False, str(erro)
