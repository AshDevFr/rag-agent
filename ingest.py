import os

from dotenv import load_dotenv

from src.sources.engine import get_new_session
from src.sources.methods import get_all_sources
from src.tools.loaders import source2Documents
from src.vector_store.pgvector import clean_store, store_docs

load_dotenv()

if __name__ == "__main__":
    # Clean the existing documents
    clean_store()

    ids = []
    with get_new_session() as session:
        sources = get_all_sources(session)
        for source in sources:
            # Store the new documents
            source_ids = store_docs(source2Documents(source))
            source.ids = source_ids
            ids += source_ids

        session.commit()

    print(f"Docs stored: {len(ids)}")
