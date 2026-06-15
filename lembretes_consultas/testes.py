# =====================================================================
# testes.py
# Testes simples para demonstrar o funcionamento do sistema em sala.
#
# Cria consultas "artificiais" com horarios calculados a partir de
# agora (faltando 7 dias, 24 horas e 3 horas) e verifica se o sistema
# identifica e "envia" os lembretes corretos. Roda em MODO_SIMULACAO.
#
# Para rodar:  python testes.py
# =====================================================================

from datetime import datetime, timedelta

from database import db_manager
from core.agendador_lembretes import processar_lembretes
from utils.logger import obter_logger

logger = obter_logger()


def _criar_consulta_teste(nome, horas_no_futuro):
    """Cria um paciente e uma consulta que ocorre 'horas_no_futuro' horas a frente."""
    email = nome.lower().replace(" ", ".") + "@teste.com"
    paciente_id = db_manager.obter_ou_criar_paciente(nome, email, "+5511999990000")
    data_hora = (datetime.now() + timedelta(hours=horas_no_futuro)).strftime("%Y-%m-%d %H:%M")
    if not db_manager.consulta_ja_existe(paciente_id, data_hora):
        db_manager.inserir_consulta(paciente_id, "Dr. Teste", "Clinica Geral", data_hora, "Sala 1")
    return data_hora


def executar_testes():
    logger.info(">>> TESTE 1: preparando banco e consultas de exemplo")
    db_manager.inicializar_banco()

    # Cria tres consultas, uma para cada janela de lembrete.
    _criar_consulta_teste("Paciente Sete Dias", 7 * 24)   # ~7 dias
    _criar_consulta_teste("Paciente Vinte Quatro", 24)    # ~24 horas
    _criar_consulta_teste("Paciente Tres Horas", 3)       # ~3 horas

    logger.info(">>> TESTE 2: primeira execucao (deve enviar 3 lembretes)")
    processados = processar_lembretes()
    assert processados >= 3, "Esperava ao menos 3 lembretes na primeira rodada"

    logger.info(">>> TESTE 3: segunda execucao (controle de duplicidade)")
    # Na segunda vez, os lembretes ja foram enviados; o sistema deve
    # reconhecer e NAO enviar de novo (verifique a mensagem 'ja enviado' no log).
    processar_lembretes()

    logger.info(">>> TODOS OS TESTES PASSARAM COM SUCESSO.")


if __name__ == "__main__":
    executar_testes()
