from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, Text, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from gst_copilot.config import DATABASE_URL

# The connection to Neon. pool_pre_ping checks the connection is alive before using it.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# A "session" is one conversation with the database. This makes new ones for us.
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Every table class inherits from this."""
    pass


class Document(Base):
    """One row = one GST PDF (a circular or a notification)."""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    doc_no: Mapped[str] = mapped_column(String(100))           # e.g. 253/10/2025-GST
    doc_type: Mapped[str] = mapped_column(String(30))          # circular / ctr_notification
    issue_date: Mapped[date | None] = mapped_column(Date)      # can be empty at first
    subject: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(5), default="en")
    source_url: Mapped[str] = mapped_column(Text, unique=True) # the PDF link, never twice
    local_path: Mapped[str | None] = mapped_column(Text)       # where we saved the PDF
    is_scanned: Mapped[bool | None]                            # filled in on Oct 11
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


def init_db() -> None:
    """Create tables that don't exist yet. Safe to run many times."""
    Base.metadata.create_all(engine)