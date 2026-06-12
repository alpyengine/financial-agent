"""Almacenamiento.

Responsabilidad única: recordar qué emails ya se procesaron para no repetirlos.
SQLAlchemy permite pasar de SQLite (MVP) a PostgreSQL (prod) cambiando solo
DATABASE_URL — misma filosofía de portabilidad que LiteLLM para la IA.
"""

from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import DateTime, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from config.settings import settings


class Base(DeclarativeBase):
    pass


class ProcessedEmail(Base):
    __tablename__ = "processed_emails"

    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    subject: Mapped[str] = mapped_column(String, default="")
    sender: Mapped[str] = mapped_column(String, default="")
    processed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# check_same_thread solo aplica a SQLite; inofensivo de declarar aquí.
_connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args)


def init_db() -> None:
    """Crea las tablas si no existen."""
    Base.metadata.create_all(engine)
    logger.info(f"Base de datos lista: {settings.DATABASE_URL}")


def filter_new(emails: list[dict]) -> list[dict]:
    """Devuelve solo los emails cuyo message_id no está aún en la base de datos."""
    if not emails:
        return []
    ids = [e["message_id"] for e in emails]
    with Session(engine) as session:
        seen = set(
            session.scalars(
                select(ProcessedEmail.message_id).where(
                    ProcessedEmail.message_id.in_(ids)
                )
            ).all()
        )
    new = [e for e in emails if e["message_id"] not in seen]
    logger.info(f"{len(new)} nuevos de {len(emails)} totales (resto ya procesados)")
    return new


def mark_processed(emails: list[dict]) -> None:
    """Marca los emails como procesados para no volver a enviarlos."""
    if not emails:
        return
    with Session(engine) as session:
        for e in emails:
            session.merge(
                ProcessedEmail(
                    message_id=e["message_id"],
                    subject=e.get("subject", ""),
                    sender=e.get("sender", ""),
                )
            )
        session.commit()
    logger.info(f"{len(emails)} emails marcados como procesados")
