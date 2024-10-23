from datetime import UTC, datetime
from hashlib import sha256
from typing import List

from sqlalchemy import ARRAY, JSON, TEXT, Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .engine import engine


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "source"
    slug: Mapped[str] = mapped_column(String(256), primary_key=True)
    meta: Mapped[dict] = Column(JSON, nullable=False)

    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    sha: Mapped[str] = mapped_column(String(64))

    ids: Mapped[List[str]] = mapped_column(ARRAY(String), default=[], nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(UTC))
    scraped_at = Column(DateTime, nullable=False, default=datetime.now(UTC))

    def __init__(self, slug: str, content: str, meta: dict) -> None:
        self.slug = slug
        self.content = content
        self.meta = meta
        self.sha = sha256(content.encode()).hexdigest()

    def __repr__(self) -> str:
        return f"Source(slug={self.slug!r})"


Base.metadata.create_all(engine)
