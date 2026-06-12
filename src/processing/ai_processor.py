"""Procesamiento con IA.

Responsabilidad única: convertir una lista de emails en un digest accionable.
Usa LiteLLM como capa de abstracción universal. NUNCA se importa openai aquí.
Cambiar de modelo/proveedor = cambiar AI_MODEL en .env, cero cambios en este fichero.
"""

from litellm import completion
from loguru import logger

from config.settings import settings

SYSTEM_PROMPT = (
    "Eres un analista financiero senior. Recibes el contenido de varios emails "
    "de newsletters financieras. Produce un digest breve y accionable en español:\n"
    "- Empieza con los 3-5 puntos más relevantes del día (mercados, tickers, eventos).\n"
    "- Sé concreto: menciona empresas, tickers y cifras cuando aparezcan.\n"
    "- Ignora promociones, publicidad y relleno.\n"
    "- Si no hay nada relevante, dilo en una sola línea.\n"
    "Formato: texto plano con viñetas simples. Sin preámbulos."
)

# Límite defensivo de caracteres por email para no desbordar el contexto del modelo.
MAX_CHARS_PER_EMAIL = 2000


def build_digest(emails: list[dict]) -> str | None:
    """Devuelve el digest en texto, o None si no hay emails que procesar."""
    if not emails:
        return None

    blocks = []
    for e in emails:
        body = (e.get("body") or "")[:MAX_CHARS_PER_EMAIL]
        blocks.append(
            f"DE: {e.get('sender', '')}\n"
            f"ASUNTO: {e.get('subject', '')}\n\n"
            f"{body}"
        )
    context = "\n\n---\n\n".join(blocks)

    logger.info(f"Enviando {len(emails)} emails al modelo {settings.AI_MODEL}")

    response = completion(
        model=settings.AI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Emails recientes:\n\n{context}"},
        ],
        temperature=0.3,
    )

    digest = response.choices[0].message.content.strip()
    logger.info(f"Digest generado ({len(digest)} caracteres)")
    return digest
