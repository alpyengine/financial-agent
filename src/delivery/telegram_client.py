"""Entrega por Telegram.

Responsabilidad única: enviar texto al chat configurado vía Bot API.
Trocea mensajes largos respetando el límite de 4096 caracteres de Telegram.

Nota de diseño: enviamos en TEXTO PLANO (sin parse_mode). El Markdown legacy de
Telegram falla con un 400 ante cualquier carácter especial suelto (_ * [ ] ( ) `),
muy frecuentes en un digest financiero generado por IA. Si más adelante quieres
formato, usa parse_mode="HTML" o "MarkdownV2" con escapado correcto.

Ante un error de la API, se loguea el cuerpo de la respuesta (que explica el
motivo exacto) antes de propagar el error al runner.
"""

import requests
from loguru import logger

from config.settings import settings

_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
_MAX_LEN = 4096


def _split(text: str, limit: int = _MAX_LEN) -> list[str]:
    """Trocea por líneas sin partir palabras cuando es posible."""
    if len(text) <= limit:
        return [text]
    chunks, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > limit:
            if current:
                chunks.append(current)
            while len(line) > limit:
                chunks.append(line[:limit])
                line = line[limit:]
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks


def send_message(text: str) -> None:
    """Envía un mensaje (troceado si es necesario) al chat de Telegram."""
    url = _API_URL.format(token=settings.TELEGRAM_BOT_TOKEN)
    chunks = _split(text)
    for i, chunk in enumerate(chunks, 1):
        resp = requests.post(
            url,
            json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": chunk,
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        if not resp.ok:
            # El cuerpo JSON de Telegram dice el motivo exacto del fallo
            # (p. ej. "chat not found" o "can't parse entities").
            logger.error(f"Telegram {resp.status_code}: {resp.text}")
            resp.raise_for_status()
        logger.info(f"Telegram: trozo {i}/{len(chunks)} enviado")
