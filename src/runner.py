"""Runner / orquestador del Financial Agent.

Encadena: Gmail -> dedup -> IA -> Telegram, y lo repite cada FETCH_INTERVAL_HOURS.
Aquí es donde los errores de los módulos se capturan y registran: un ciclo que
falla se loguea con traza completa y el agente sigue vivo para el siguiente ciclo.
"""

import time

import schedule
from loguru import logger

from config.settings import settings
from src.delivery.telegram_client import send_message
from src.ingestion.gmail_client import fetch_recent_emails
from src.processing.ai_processor import build_digest
from src.storage import database

APP_VERSION = "0.2.0"


def run_cycle() -> None:
    """Un ciclo completo de ingesta -> procesamiento -> entrega."""
    logger.info("=== Ciclo iniciado ===")

    emails = fetch_recent_emails()
    new_emails = database.filter_new(emails)

    if not new_emails:
        logger.info("Sin emails nuevos. Nada que enviar.")
        return

    digest = build_digest(new_emails)
    if not digest:
        logger.info("El modelo no devolvió digest. Marcando emails como vistos.")
        database.mark_processed(new_emails)
        return

    send_message(f"📊 Digest financiero\n\n{digest}")
    database.mark_processed(new_emails)
    logger.success(f"Digest enviado ({len(new_emails)} emails)")


def safe_cycle() -> None:
    """Envuelve run_cycle: registra cualquier error sin tumbar el scheduler."""
    try:
        run_cycle()
    except Exception:
        logger.exception("El ciclo falló — se reintentará en el próximo intervalo")


def main() -> None:
    logger.add(
        "data/financial_agent.log",
        rotation="10 MB",
        retention="14 days",
        level="INFO",
    )
    database.init_db()
    logger.info(
        f"Financial Agent v{APP_VERSION} | modelo={settings.AI_MODEL} | "
        f"cada {settings.FETCH_INTERVAL_HOURS}h"
    )

    # Primer ciclo inmediato al arrancar (no esperamos 5h para la primera ejecución).
    safe_cycle()

    schedule.every(settings.FETCH_INTERVAL_HOURS).hours.do(safe_cycle)
    logger.info("Scheduler activo. Esperando próximos ciclos…")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
