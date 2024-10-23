import os

from src.scrapers.discourse import client as discourse_client
from dotenv import load_dotenv

from src.sources.engine import get_new_session
from src.sources.methods import upsert_source
from src.scrapers.gitlab import client as gitlab_client

load_dotenv()

if __name__ == "__main__":
    with get_new_session() as session:
        gitlab_sources = gitlab_client.getSources()

        for source in gitlab_sources:
            upsert_source(session, source)

        print(f"GitLab wiki pages found: {len(gitlab_sources)}")

        session.commit()

    with get_new_session() as session:
        discourse_sources = discourse_client.getSources()
        for source in discourse_sources:
            upsert_source(session, source)

        print(f"Discourse topics found: {len(discourse_sources)}")

        session.commit()
