# Sistema Automatizado de Lembretes de Consultas (E-mail e WhatsApp)

Sistema em Python que lê consultas de uma planilha Excel, armazena em um
banco SQLite e envia lembretes automáticos por **e-mail** e **WhatsApp**
em três momentos: **7 dias**, **24 horas** e **3 horas** antes da consulta.

## Estrutura do projeto

```
lembretes_consultas/
├── config.py                  # configurações (SMTP, Twilio, regras)
├── main.py                    # executa uma rodada completa
├── scheduler.py               # mantém o sistema rodando (a cada 1h)
├── testes.py                  # testes de demonstração
├── requirements.txt           # dependências
├── consultas_exemplo.xlsx     # planilha de exemplo
├── database/
│   ├── schema.sql             # criação das tabelas
│   └── db_manager.py          # acesso ao banco (DAO)
├── core/
│   ├── importador_excel.py    # leitura da planilha
│   ├── agendador_lembretes.py # lógica dos lembretes + duplicidade
│   ├── enviador_email.py      # envio por e-mail (SMTP)
│   └── enviador_whatsapp.py   # envio por WhatsApp (Twilio)
└── utils/
    └── logger.py              # configuração de logs
```

## Passo a passo de instalação

1. Instale o Python 3.10 ou superior (https://www.python.org).
2. Abra o terminal na pasta do projeto.
3. (Opcional, recomendado) crie um ambiente virtual:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Como executar

- **Rodar uma vez** (importa a planilha e envia os lembretes devidos):
  ```bash
  python main.py
  ```
- **Rodar de forma contínua** (a cada 1 hora):
  ```bash
  python scheduler.py
  ```
- **Rodar os testes de demonstração**:
  ```bash
  python testes.py
  ```

## Modo de simulação

No arquivo `config.py`, a opção `MODO_SIMULACAO = True` faz o sistema
apenas registrar no log o que seria enviado, sem disparar mensagens reais.
Ideal para apresentar o projeto em sala sem precisar de credenciais.

Para enviar de verdade, altere para `MODO_SIMULACAO = False` e preencha:
- **E-mail:** `EMAIL_REMETENTE` e `EMAIL_SENHA` (no Gmail, use uma *senha de app*).
- **WhatsApp:** `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` e `TWILIO_WHATSAPP_FROM`
  (obtidos no painel da Twilio; o sandbox é gratuito).

## Formato da planilha Excel

A primeira linha deve conter os cabeçalhos (exatamente estes nomes):

| paciente | email | telefone | medico | especialidade | data_hora | local |
|----------|-------|----------|--------|---------------|-----------|-------|

A coluna `data_hora` deve estar no formato `AAAA-MM-DD HH:MM`
(exemplo: `2026-06-15 14:30`).
