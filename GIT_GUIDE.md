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
