"""Ingesta de Gmail.

Responsabilidad única: autenticarse contra Gmail y devolver los emails
financieros recientes como una lista de dicts. No resume, no decide, no guarda.
Los errores se propagan al runner (este módulo no los silencia).
"""

import base64
import os
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger

from config.settings import settings

# Solo lectura: el agente nunca modifica el buzón.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _get_service():
    """Devuelve un servicio autenticado de la Gmail API.

    Primer arranque: abre el navegador para el consentimiento OAuth y guarda el
    token en GMAIL_TOKEN_FILE. Arranques posteriores: reutiliza/renueva el token.
    """
    creds = None
    token_path = settings.GMAIL_TOKEN_FILE

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Token de Gmail expirado, renovando…")
            creds.refresh(Request())
        else:
            logger.info("Sin token válido. Iniciando flujo OAuth en el navegador…")
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GMAIL_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(token_path) or ".", exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        logger.info(f"Token de Gmail guardado en {token_path}")

    return build("gmail", "v1", credentials=creds)


def _extract_body(payload) -> str:
    """Recorre el árbol MIME y devuelve el primer texto plano encontrado."""

    def decode(data: str) -> str:
        return base64.urlsafe_b64decode(data.encode("utf-8")).decode(
            "utf-8", errors="replace"
        )

    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            return decode(data)

    for part in payload.get("parts", []) or []:
        text = _extract_body(part)
        if text:
            return text

    # Fallback: si solo hay HTML, devolvemos algo en vez de nada.
    if payload.get("mimeType") == "text/html":
        data = payload.get("body", {}).get("data")
        if data:
            return decode(data)

    return ""


def fetch_recent_emails() -> list[dict]:
    """Devuelve los emails financieros de las últimas LOOKBACK_HOURS horas."""
    service = _get_service()

    after_ts = int(
        (datetime.now(timezone.utc) - timedelta(hours=settings.LOOKBACK_HOURS)).timestamp()
    )
    query = f"{settings.GMAIL_QUERY} after:{after_ts}"
    logger.info(f"Gmail query: {query}")

    resp = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=50)
        .execute()
    )
    message_refs = resp.get("messages", [])
    logger.info(f"Gmail: {len(message_refs)} mensajes coinciden")

    emails: list[dict] = []
    for ref in message_refs:
        full = (
            service.users()
            .messages()
            .get(userId="me", id=ref["id"], format="full")
            .execute()
        )
        headers = {
            h["name"].lower(): h["value"]
            for h in full.get("payload", {}).get("headers", [])
        }
        emails.append(
            {
                "message_id": ref["id"],
                "subject": headers.get("subject", "(sin asunto)"),
                "sender": headers.get("from", ""),
                "date": headers.get("date", ""),
                "body": _extract_body(full.get("payload", {})).strip(),
            }
        )

    return emails
