import os

from src.scrapers.discourse import client as discourse_client
from dotenv import load_dotenv

from src.sources.engine import get_new_session
from src.sources.methods import get_source, update_existing_source
from src.scrapers.gitlab import client as gitlab_client
from src.tools.loaders import source2Documents
from src.vector_store.pgvector import delete_docs, store_docs

load_dotenv()

if __name__ == "__main__":
    with get_new_session() as session:
        gitlab_ids = []
        gitlab_sources = gitlab_client.getSources()
        for source in gitlab_sources:
            existing_source = get_source(session, source.slug)
            if existing_source:
                if update_existing_source(existing_source, source):
                    # Clean the existing documents
                    delete_docs(existing_source.ids)
                    # Store the new documents
                    source_ids = store_docs(source2Documents(source))
                    existing_source.ids = source_ids
                    gitlab_ids += source_ids
            else:
                source_ids = store_docs(source2Documents(source))
                source.ids = source_ids
                session.add(source)
                gitlab_ids += source_ids

        session.commit()

        print(f"GitLab wiki pages found: {len(gitlab_sources)}")
        print(f"GitLab docs stored: {len(gitlab_ids)}")

    with get_new_session() as session:
        discourse_ids = []
        discourse_sources = discourse_client.getSources()
        for source in discourse_sources:
            existing_source = get_source(session, source.slug)
            if existing_source:
                if update_existing_source(existing_source, source):
                    # Clean the existing documents
                    delete_docs(existing_source.ids)
                    # Store the new documents
                    source_ids = store_docs(source2Documents(source))
                    existing_source.ids = source_ids
                    discourse_ids += source_ids
            else:
                source_ids = store_docs(source2Documents(source))
                source.ids = source_ids
                session.add(source)
                discourse_ids += source_ids

        print(f"Discourse topics found: {len(discourse_sources)}")
        print(f"Discourse docs stored: {len(discourse_ids)}")

        session.commit()
