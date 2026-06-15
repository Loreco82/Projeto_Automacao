# =====================================================================
# scheduler.py
# Mantem o sistema rodando sozinho, executando uma rodada de tempos
# em tempos (por padrao, a cada 1 hora).
#
# Usa a biblioteca 'schedule', simples e ideal para fins didaticos.
# Em ambientes de producao tambem e comum usar o 'cron' (Linux) ou o
# Agendador de Tarefas (Windows) chamando o main.py diretamente.
#
# Para rodar:  python scheduler.py   (e deixar a janela aberta)
# =====================================================================

import time

import schedule

from main import executar_rodada
from utils.logger import obter_logger

logger = obter_logger()


def iniciar_agendador():
    """Configura e inicia o loop de agendamento."""
    logger.info("Agendador iniciado. O sistema rodara a cada 1 hora.")

    # Executa uma rodada imediatamente ao iniciar (para nao esperar 1h).
    executar_rodada()

    # Agenda a repeticao. Pode-se ajustar para .minutes, .days etc.
    schedule.every(1).hours.do(executar_rodada)

    # Loop infinito: verifica a cada 60s se chegou a hora de rodar.
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        iniciar_agendador()
    except KeyboardInterrupt:
        # Permite encerrar com Ctrl+C de forma limpa.
        logger.info("Agendador encerrado pelo usuario.")
