# automacao_nf_boleto — Documentação para o Claude

Este arquivo serve como contexto persistente para sessões do Claude Code.
Leia-o antes de qualquer intervenção no projeto.

---

## Visão Geral do Fluxo

```
Telegram (cliente) — @Chacaraejardimbot
    │
    ▼
Webhook Flask  (app.py)
    │  recebe mensagem, extrai CNPJ/dados via parse_mensagem()
    ▼
automacao.py   (orquestra tudo)
    ├── Playwright → ISS (emite NF)
    ├── API Cora   → gera boleto (mTLS)
    └── Google Sheets/Drive → registra + envia docs
```

O ponto de entrada de produção é o **webhook Flask** (`app.py`).
O `automacao.py` é chamado por ele em uma thread separada e executa as três etapas em sequência.

---

## Estrutura de Arquivos

```
automacao_nf_boleto/
├── CLAUDE.md            # Este arquivo — contexto do projeto
├── app.py               # Servidor Flask: recebe webhook Telegram, chama automacao.py
├── automacao.py         # Orquestrador principal do fluxo NF → Boleto → Drive
├── iss_nf.py            # Módulo Playwright para emissão de NF no portal ISS
├── cora_boleto.py       # Módulo para geração de boleto via API Cora (mTLS)
├── google_drive.py      # Upload de PDFs e registro em Google Sheets (OAuth)
├── dashboard.py         # Dashboard web com SSE para monitoramento em tempo real
├── requirements.txt     # Dependências Python
├── .env                 # Credenciais (nunca commitar)
├── certs/
│   ├── cora_cert.pem    # Certificado mTLS Cora (cliente)
│   └── cora_key.pem     # Chave privada mTLS Cora
└── credentials/
    └── google_sa.json   # Service Account Google (OAuth)
```

---

## Detalhes Técnicos Críticos

### 1. Portal ISS — RichFaces/AJAX (`iss_nf.py`)

- O portal ISS usa **RichFaces 4** com requests AJAX pesadas.
- Campos de formulário disparam eventos `a4j:ajax` que atualizam partes da página — simular `click()` direto muitas vezes não funciona.
- A sequência correta é:
  1. Preencher campo
  2. Disparar `change` + `blur` via `page.evaluate()`
  3. Aguardar o seletor do próximo campo aparecer antes de continuar
- **Timeouts longos são normais** — o portal é lento; não reduza os `wait_for_selector` abaixo de 10 s.
- O login usa sessão de cookie; re-login automático está implementado ao detectar redirect para `/login`.

### 2. API Cora — mTLS (`cora_boleto.py`)

- A Cora exige **mutual TLS** (certificado do cliente).
- Os certificados ficam em `certs/cora_cert.pem` e `certs/cora_key.pem`.
- Uso com `httpx`:
  ```python
  client = httpx.Client(cert=("certs/cora_cert.pem", "certs/cora_key.pem"))
  ```
- O token de acesso OAuth 2.0 da Cora expira em 1 h — há renovação automática em `cora_boleto.py`.
- **Ambiente de produção vs. sandbox**: a URL base está em `.env` como `CORA_BASE_URL`.

### 3. Google Drive / Sheets — OAuth (`google_drive.py`)

- Usa **Service Account** (não OAuth interativo) — arquivo em `credentials/google_sa.json`.
- A SA precisa ter acesso compartilhado à planilha e à pasta do Drive.
- Scopes necessários:
  - `https://www.googleapis.com/auth/drive`
  - `https://www.googleapis.com/auth/spreadsheets`
- PDFs de NF e boleto são uploadados para uma pasta específica no Drive (ID em `.env` como `GDRIVE_FOLDER_ID`).

### 4. Dashboard — SSE (`dashboard.py`)

- O dashboard usa **Server-Sent Events** (SSE) para atualização em tempo real.
- O endpoint `/stream` mantém conexão aberta e empurra eventos conforme o `automacao.py` progride.
- **Não use `threading` para comunicar com o SSE** — use a `queue.Queue` já implementada.
- Frontend conecta via `EventSource('/stream')` em JavaScript puro (sem framework).

---

## O que NÃO Fazer

### Playwright / ISS (`iss_nf.py`)

- **Não simplifique a sequência de cliques** — ela foi calibrada empiricamente contra o RichFaces.
- **Não remova os `await asyncio.sleep()`** entre ações no ISS — o portal precisa de tempo para processar AJAX antes do próximo passo.
- **Não troque `page.evaluate()` por `locator.click()`** em campos que têm listeners AJAX — o evento não propaga corretamente.
- **Não altere os seletores CSS** sem testar — o ISS muda layout sem aviso.

### Geral

- **Não commite `.env` ou `certs/` ou `credentials/`** — estão no `.gitignore`.
- **Não rode `automacao.py` diretamente em produção** sem desligar o webhook Flask primeiro (evita execuções paralelas).
- **Não modifique `requirements.txt` manualmente** — use `pip freeze > requirements.txt` após instalar.

---

## Variáveis de Ambiente (`.env`)

```
# ISS
ISS_URL=https://nfse.SUACIDADE.gov.br
ISS_USER=...
ISS_PASS=...

# Cora
CORA_BASE_URL=https://matls-clients.api.cora.com.br
CORA_CLIENT_ID=...
CORA_CLIENT_SECRET=...

# Google
GDRIVE_FOLDER_ID=...
GSHEET_ID=...

# Telegram
TELEGRAM_TOKEN=...              # Token do @BotFather
TELEGRAM_CHAT_ID=...            # (opcional) restringe a um chat_id específico
```

---

## Próximos Passos Pendentes

- [ ] **Registrar webhook Telegram** *(passo manual — requer URL pública)*:
      ```bash
      # Em dev: expor com ngrok
      ngrok http 5000
      # Copiar a URL HTTPS gerada (ex: https://abc123.ngrok-free.app) e rodar:
      curl "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook" \
           -d "url=https://abc123.ngrok-free.app/webhook/$TELEGRAM_TOKEN"

      # Verificar se registrou corretamente:
      curl "https://api.telegram.org/bot$TELEGRAM_TOKEN/getWebhookInfo"
      ```
      Em produção substituir a URL ngrok pelo domínio real (HTTPS obrigatório).
- [x] Implementar `automacao.py` e integrá-lo ao `app.py` via callback de progresso.
- [x] Retry automático em caso de falha no ISS — backoff exponencial (2 s, 4 s, 8 s), até 3 tentativas (`MAX_RETRIES` em `iss_nf.py`).
- [x] Notificação de erro via Telegram — cada etapa lança `RuntimeError` com contexto; `app.py` captura e envia a mensagem ao usuário.
- [ ] Testes de integração com o sandbox da Cora — arquivo criado em `tests/test_cora_sandbox.py`; requer credenciais sandbox configuradas no `.env`.

---

## Como Rodar Localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt
playwright install chromium

# 2. Configurar .env (copiar do modelo acima)

# 3. Rodar o Flask (desenvolvimento)
flask --app app.py run --port 5000

# 4. Expor via ngrok para registrar o webhook Telegram
ngrok http 5000

# 5. Registrar webhook no Telegram (só precisa fazer uma vez por URL)
curl "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook?url=https://SEU_NGROK/webhook/$TELEGRAM_TOKEN"
```

---

## Contato / Contexto de Negócio

- Projeto pessoal para automatizar emissão de NF e boleto para clientes.
- Fluxo iniciado quando cliente manda mensagem no WhatsApp com os dados da prestação de serviço.
- Resultado final: NF emitida no ISS municipal + boleto Cora gerado + ambos enviados ao cliente e registrados no Drive.
