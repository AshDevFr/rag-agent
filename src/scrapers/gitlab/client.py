import logging
import os
from typing import List

import gitlab
from dotenv import load_dotenv

from src.sources.models import Source

load_dotenv()

log = logging.getLogger("gitlab.client")


def _fetchWikiPages():
    # Create a GitLab client instance
    gl = gitlab.Gitlab(
        url=os.environ.get("GITLAB_HOST"), private_token=os.environ.get("GITLAB_TOKEN")
    )

    pages = []
    # Get all projects
    projects = gl.projects.list(get_all=True)

    # Get all wiki pages from all projects
    for project in projects:
        if not project.wiki_enabled or project.archived:
            continue

        log.debug(f"Fetching wiki pages for {project.name}")
        project_wiki_pages = project.wikis.list()
        for p in project_wiki_pages:
            url = f"{project.web_url}/-/wikis/{p.slug}"
            log.debug(f"  - {p.slug} ({url})")

            page = project.wikis.get(p.slug)
            page.url = url
            page.full_slug = f"{project.path_with_namespace}/{page.slug}"
            pages.append(page)

    return pages


def getSources() -> List[Source]:
    sources = []
    # Get all wiki pages
    pages = _fetchWikiPages()
    for page in pages:
        meta = {"url": page.url, "title": page.title}

        sources.append(
            Source(slug=f"gitlab/{page.full_slug}", content=page.content, meta=meta)
        )

    return sources


if __name__ == "__main__":
    sources = getSources()
    print(f"Found {len(sources)} documents")
