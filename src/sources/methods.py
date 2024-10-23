from datetime import UTC, datetime
from typing import List, Type

from sqlalchemy.orm import Session

from .models import Source


def get_all_sources(session: Session) -> List[Type[Source]]:
    return session.query(Source).all()


def get_source(session: Session, slug: str) -> Source | None:
    return session.query(Source).filter(Source.slug == slug).first()


def update_existing_source(existing_source: Source, source: Source) -> bool:
    existing_source.scraped_at = datetime.now(UTC)
    if existing_source.sha == source.sha:
        return False

    existing_source.meta = source.meta
    existing_source.content = source.content
    existing_source.sha = source.sha
    existing_source.updated_at = datetime.now(UTC)
    return True


def upsert_source(session: Session, source: Source) -> bool:
    existing_source = session.query(Source).filter(Source.slug == source.slug).first()
    if existing_source:
        return update_existing_source(existing_source, source)

    else:
        session.add(source)
        return True
