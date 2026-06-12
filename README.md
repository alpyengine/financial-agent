# Financial Agent

> Agente de inteligencia financiera en Python: lee newsletters de Gmail, los procesa con IA vía LiteLLM y entrega un digest accionable por Telegram.

## 1. Descripción del proyecto

**Financial Agent** automatiza la lectura de correos financieros (Seeking Alpha, Investing.com, etc.) que llegan a Gmail, los resume y clasifica con un LLM, y envía un **digest diario estructurado** a un chat de Telegram.

El objetivo es eliminar la investigación financiera repetitiva y servir además como ejemplo didáctico de arquitectura de agentes de IA. El stack del MVP es **100% gratuito y open source**.

- **Problema que resuelve:** revisar manualmente decenas de newsletters financieros cada día.
- **Usuario objetivo:** un inversor/analista que quiere un resumen accionable sin abrir la bandeja.
- **Resultado esperado:** un digest por Telegram cada 5 horas con lo relevante del correo financiero reciente.

## 2. Stack tecnológico

- **Lenguaje:** Python 3.11+
- **Capa IA:** [LiteLLM](https://github.com/BerriAI/litellm) como abstracción universal (nunca se importa `openai` directamente)
- **Modelo MVP:** `groq/llama-3.1-8b-instant` (Groq free tier)
- **Base de datos:** SQLite (MVP) → PostgreSQL (producción)
- **Entrega:** Telegram Bot API
- **Fuente de email:** Gmail API (OAuth, scope `gmail.readonly`)
- **Automatización:** Docker + `schedule`
- **Logging:** loguru

## 3. Instalación y puesta en marcha

```bash
# 1. Clonar el repositorio
git clone https://github.com/alpyengine/financial-agent.git
cd financial-agent

# 2. Crear y activar el entorno virtual
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env             # luego edita .env con tus valores reales

# 5. Colocar las credenciales de Gmail
#    Descarga credentials.json desde Google Cloud Console (cliente OAuth Desktop)
#    y déjalo en la raíz del proyecto.

# 6. Ejecutar (primera vez: abrirá el navegador para autorizar Gmail
#    y generará data/gmail_token.json automáticamente)
python -m src.runner
```

> El despliegue en producción se hará vía Docker (programado cada 5 horas).

## 4. Variables de entorno / configuración necesaria

Copia `.env.example` a `.env` y rellena:

```
AI_MODEL=groq/llama-3.1-8b-instant   # cambiar de modelo = solo esta línea
GROQ_API_KEY=...                     # console.groq.com → API Keys
TELEGRAM_BOT_TOKEN=...               # @BotFather → /newbot
TELEGRAM_CHAT_ID=...                 # vía getUpdates
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=data/gmail_token.json
DATABASE_URL=sqlite:///data/financial_agent.db
```

**Nunca** se commitean `.env`, `credentials.json` ni `data/gmail_token.json` (excluidos en `.gitignore`).

## 5. Changelog

| Versión | Descripción del cambio |
|---------|-----------------------------------------------------|
| v0.2.0  | feat: MVP funcional — Gmail → LiteLLM → digest → Telegram (cada 5h) |
| v0.1.0  | chore: inicialización del proyecto (estructura base, Git, documentación) |
