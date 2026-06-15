# =====================================================================
# main.py
# Ponto de entrada do sistema (executa UMA rodada completa).
#
# Fluxo:
#   1. Garante que o banco e as tabelas existem;
#   2. Importa as consultas da planilha Excel;
#   3. Verifica e envia os lembretes devidos.
#
# Para rodar:  python main.py
# =====================================================================

from database import db_manager
from core.importador_excel import importar_consultas
from core.agendador_lembretes import processar_lembretes
from utils.logger import obter_logger

logger = obter_logger()


def executar_rodada():
    """Executa o ciclo completo do sistema uma unica vez."""
    logger.info("=" * 60)
    logger.info("INICIANDO RODADA DO SISTEMA DE LEMBRETES")
    logger.info("=" * 60)

    try:
        # Etapa 1 - prepara o banco (cria tabelas se necessario).
        db_manager.inicializar_banco()

        # Etapa 2 - le a planilha e cadastra as consultas novas.
        importar_consultas()

        # Etapa 3 - envia os lembretes que estiverem na janela de tempo.
        processar_lembretes()

    except Exception as erro:
        # Erro inesperado: registra e nao deixa o programa "quebrar feio".
        logger.exception("Erro inesperado durante a rodada: %s", erro)

    logger.info("RODADA FINALIZADA.\n")


if __name__ == "__main__":
    executar_rodada()
