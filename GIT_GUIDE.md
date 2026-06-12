# ===========================================================================
# GIT_GUIDE.md — Financial Agent
# ===========================================================================
#
# REPOSITORY:
#   GitHub: https://github.com/alpyengine/financial-agent.git
#   Local:  ~/Projects/financial-agent/
#   Description: Agente de inteligencia financiera en Python: lee Gmail,
#                procesa con IA (LiteLLM) y entrega un digest por Telegram.
#
# Convención: Conventional Commits. Rama principal: main.
# Cada versión = un STEP numerado (no se reinicia la numeración entre versiones).
# ===========================================================================


# ===========================================================================
# STEP 1 — v0.1.0  Inicialización del proyecto
# ===========================================================================
#
# WHAT'S NEW:
#   README.md      — documentación inicial (Bloque 7: 5 secciones + changelog)
#   .gitignore     — exclusión de .env, credentials.json y data/ (secretos)
#   GIT_GUIDE.md   — guía de commits por STEP
#   .env.example   — plantilla de variables de entorno
#   data/.gitkeep  — preserva la carpeta data/ (DB + token quedan ignorados)
#
# MIGRATIONS:
#   - Copiar .env.example a .env y rellenar valores reales.
#   - Colocar credentials.json (cliente OAuth Desktop) en la raíz del proyecto.
#   - El token data/gmail_token.json se genera solo en la primera ejecución.
#
# Comandos listos para copiar/pegar:

cd ~/Projects/financial-agent

# Config Git LOCAL por proyecto (omitir si ya está configurada)
git init
git branch -M main
git config user.name  "alpyengine"
git config user.email "alpyengine@gmail.com"
git config --list --local        # verificar

# Conexión con el remoto (crea antes el repo vacío en GitHub)
git remote add origin https://github.com/alpyengine/financial-agent.git
git remote -v                    # verificar

# Primer commit + tag + push
git add .
git commit -m "chore: project init (v0.1.0)

README.md:
Documentación inicial del proyecto (descripción, stack, instalación, variables, changelog).

.gitignore:
Exclusión de secretos (.env, credentials.json) y contenido de data/.

GIT_GUIDE.md:
Guía de commits por STEP siguiendo el marco Git del proyecto.

.env.example:
Plantilla de variables de entorno con AI_MODEL corregido a groq/llama-3.1-8b-instant."

git tag -a v0.1.0 -m "v0.1.0: inicialización del proyecto"
git push -u origin main
git push origin v0.1.0

# VERIFICACIÓN
git log --oneline
git tag -l


# ===========================================================================
# STEP 2 — v0.2.0  MVP funcional (Gmail -> LiteLLM -> digest -> Telegram)
# ===========================================================================
#
# WHAT'S NEW:
#   requirements.txt                  — dependencias (litellm, google-api, sqlalchemy, etc.)
#   config/settings.py                — config central; AI_MODEL como única variable de modelo
#   src/runner.py                     — orquestador + scheduler cada 5h (ejecutar con -m)
#   src/ingestion/gmail_client.py     — lectura de Gmail (OAuth, scope readonly)
#   src/processing/ai_processor.py    — resumen vía LiteLLM (Groq), patrón obligatorio
#   src/storage/database.py           — deduplicación en SQLite (SQLAlchemy)
#   src/delivery/telegram_client.py   — entrega por Telegram Bot API (texto plano, troceo 4096)
#   Dockerfile, docker-compose.yml    — despliegue
#   config/__init__.py, src/**/__init__.py — paquetes Python
#
# NOTAS / LECCIONES DE ESTA VERSIÓN:
#   - Telegram devolvía HTTP 400 al usar parse_mode="Markdown": el Markdown
#     legacy de Telegram rompe ante caracteres especiales sueltos (_ * [ ] ( ) `),
#     habituales en un digest generado por IA. Solución: enviar en TEXTO PLANO
#     (sin parse_mode) y loguear el cuerpo de error de la API para diagnóstico.
#   - El antiguo modelo groq/llama3-8b-8192 fue descatalogado por Groq;
#     se usa groq/llama-3.1-8b-instant (cambio de una línea en .env).
#
# MIGRATIONS:
#   - El primer arranque (python -m src.runner) abre el navegador para el OAuth
#     de Gmail y genera data/gmail_token.json. Hacerlo en local, no en Docker.
#   - La app OAuth de Google debe tener tu cuenta como "usuario de prueba".
#
# Comandos listos para copiar/pegar:

cd ~/Projects/financial-agent

git add .
git commit -m "feat: MVP funcional Gmail -> IA -> Telegram (v0.2.0)

requirements.txt:
Dependencias del MVP: litellm, google-api-python-client, sqlalchemy, requests, loguru, schedule.

config/settings.py:
Configuracion central con pydantic-settings. AI_MODEL como unica palanca de modelo.

src/runner.py:
Orquestador. Encadena ingesta -> dedup -> IA -> entrega; scheduler cada 5h.
Los errores de los modulos suben aqui y se loguean sin tumbar el agente.

src/ingestion/gmail_client.py:
Lectura de Gmail via OAuth (scope readonly) y parseo de cuerpos MIME.

src/processing/ai_processor.py:
Resumen con LiteLLM (from litellm import completion, model=settings.AI_MODEL).

src/storage/database.py:
Deduplicacion por message_id en SQLite via SQLAlchemy.

src/delivery/telegram_client.py:
Envio por Telegram Bot API en texto plano (evita el 400 de Markdown), troceo a 4096.

Dockerfile / docker-compose.yml:
Despliegue del agente en contenedor."

git tag -a v0.2.0 -m "v0.2.0: MVP funcional"
git push origin main
git push origin v0.2.0

# VERIFICACIÓN
git log --oneline
git tag -l
