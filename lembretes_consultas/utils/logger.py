# =====================================================================
# utils/logger.py
# Configura o sistema de logs (registro de eventos).
#
# O log e essencial em qualquer sistema automatizado: como ele roda
# sozinho, sem ninguem olhando, os registros sao a unica forma de saber
# o que aconteceu (sucessos, falhas, erros).
# =====================================================================

import logging
import sys

# Importa o caminho do arquivo de log definido no config.py.
# O "import" abaixo funciona porque executamos o sistema a partir da
# pasta raiz do projeto (onde fica o config.py).
from config import CAMINHO_LOG


def obter_logger(nome="lembretes"):
    """Cria (ou recupera) um logger ja configurado.

    O logger grava as mensagens em DOIS lugares ao mesmo tempo:
      1. No arquivo lembretes.log (para historico permanente);
      2. No terminal/console (para acompanhar a execucao em tempo real).
    """
    logger = logging.getLogger(nome)

    # Evita adicionar os mesmos "handlers" varias vezes se a funcao
    # for chamada mais de uma vez durante a execucao.
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Formato de cada linha de log: data/hora - nivel - mensagem.
    formato = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler 1: grava no arquivo.
    arquivo = logging.FileHandler(CAMINHO_LOG, encoding="utf-8")
    arquivo.setFormatter(formato)
    logger.addHandler(arquivo)

    # Handler 2: mostra no console.
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formato)
    logger.addHandler(console)

    return logger
