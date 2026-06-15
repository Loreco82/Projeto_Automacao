# =====================================================================
# config.py
# Centraliza todas as configurações do sistema em um único lugar.
#
# Em produção, o ideal é ler esses valores de variáveis de ambiente
# (os.getenv) para nao expor senhas no codigo. Para facilitar o estudo
# em sala, deixamos os valores aqui com instrucoes claras.
# =====================================================================

import os

# ----- Caminhos de arquivos -----
# Diretorio raiz do projeto (a pasta onde este arquivo esta).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho do banco de dados SQLite.
CAMINHO_BANCO = os.path.join(BASE_DIR, "lembretes.db")

# Caminho do script de criacao das tabelas.
CAMINHO_SCHEMA = os.path.join(BASE_DIR, "database", "schema.sql")

# Planilha Excel de onde as consultas serao importadas.
CAMINHO_EXCEL = os.path.join(BASE_DIR, "consultas_exemplo.xlsx")

# Arquivo de log do sistema.
CAMINHO_LOG = os.path.join(BASE_DIR, "lembretes.log")


# ----- Configuracoes de E-mail (SMTP) -----
# Exemplo usando Gmail. Para o Gmail, e necessario gerar uma
# "senha de app" (App Password), pois a senha normal nao funciona.
EMAIL_SMTP_SERVIDOR = "smtp.gmail.com"
EMAIL_SMTP_PORTA = 587
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "clinica.exemplo@gmail.com")
EMAIL_SENHA = os.getenv("EMAIL_SENHA", "coloque_sua_senha_de_app_aqui")
EMAIL_NOME_EXIBICAO = "Clinica Exemplo"


# ----- Configuracoes do WhatsApp (Twilio) -----
# A Twilio oferece um sandbox gratuito do WhatsApp para testes.
# Os tres valores abaixo sao obtidos no painel da Twilio.
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "seu_auth_token_aqui")
# Numero do WhatsApp da Twilio (no sandbox costuma ser este).
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"


# ----- Regras de negocio dos lembretes -----
# Cada tupla define: (codigo do lembrete, antecedencia em horas, tolerancia em horas).
# A tolerancia (janela) garante que, mesmo que o sistema rode de hora
# em hora, o lembrete seja disparado dentro de um intervalo aceitavel.
REGRAS_LEMBRETES = [
    ("7d", 7 * 24, 12),   # 7 dias antes  (tolerancia de 12h)
    ("24h", 24, 2),       # 24 horas antes (tolerancia de 2h)
    ("3h", 3, 1),         # 3 horas antes  (tolerancia de 1h)
]

# Texto amigavel para cada tipo de lembrete (usado nas mensagens).
DESCRICAO_LEMBRETE = {
    "7d": "faltam 7 dias",
    "24h": "falta 1 dia",
    "3h": "faltam 3 horas",
}

# Liga/desliga o modo de simulacao. Quando True, o sistema NAO envia
# e-mails/WhatsApp de verdade: apenas registra no log o que seria enviado.
# Util para apresentar o projeto em sala sem precisar de credenciais reais.
MODO_SIMULACAO = True
