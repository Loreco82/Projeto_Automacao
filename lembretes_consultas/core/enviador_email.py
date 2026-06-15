# =====================================================================
# core/enviador_email.py
# Responsavel por montar e enviar os lembretes por e-mail (protocolo SMTP).
#
# Usa apenas bibliotecas padrao do Python (smtplib e email), sem precisar
# instalar nada extra para o e-mail.
# =====================================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    EMAIL_SMTP_SERVIDOR, EMAIL_SMTP_PORTA,
    EMAIL_REMETENTE, EMAIL_SENHA, EMAIL_NOME_EXIBICAO,
    MODO_SIMULACAO,
)
from utils.logger import obter_logger

logger = obter_logger()


def montar_mensagem(consulta, descricao_lembrete):
    """Monta o texto do e-mail a partir dos dados da consulta."""
    return (
        f"Ola, {consulta['paciente']}!\n\n"
        f"Este e um lembrete da sua consulta. {descricao_lembrete.capitalize()}.\n\n"
        f"Especialidade: {consulta['especialidade']}\n"
        f"Profissional: {consulta['medico']}\n"
        f"Data e hora: {consulta['data_hora']}\n"
        f"Local: {consulta['local']}\n\n"
        f"Em caso de imprevisto, entre em contato para remarcar.\n\n"
        f"Atenciosamente,\n{EMAIL_NOME_EXIBICAO}"
    )


def enviar_email(consulta, descricao_lembrete):
    """Envia um e-mail de lembrete.

    Retorna uma tupla (sucesso: bool, detalhe: str).
    Quando MODO_SIMULACAO esta ligado, apenas registra no log o que seria
    enviado, sem conectar de fato ao servidor.
    """
    destinatario = consulta["email"]
    assunto = "Lembrete de consulta"
    corpo = montar_mensagem(consulta, descricao_lembrete)

    if MODO_SIMULACAO:
        logger.info("[SIMULACAO] E-mail para %s | %s", destinatario, descricao_lembrete)
        return True, "simulado"

    try:
        # Monta o e-mail com remetente, destinatario, assunto e corpo.
        mensagem = MIMEMultipart()
        mensagem["From"] = f"{EMAIL_NOME_EXIBICAO} <{EMAIL_REMETENTE}>"
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto
        mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

        # Abre a conexao segura (TLS) com o servidor SMTP e envia.
        with smtplib.SMTP(EMAIL_SMTP_SERVIDOR, EMAIL_SMTP_PORTA) as servidor:
            servidor.starttls()                    # ativa a criptografia
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.send_message(mensagem)

        logger.info("E-mail enviado para %s.", destinatario)
        return True, "enviado"

    except Exception as erro:
        # Captura qualquer falha (servidor fora do ar, senha errada etc.).
        logger.error("Falha ao enviar e-mail para %s: %s", destinatario, erro)
        return False, str(erro)
