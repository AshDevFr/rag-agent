import logging
import os
import time
from typing import List

import requests
from dotenv import load_dotenv
from pydiscourse import DiscourseClient
from pydiscourse.exceptions import (DiscourseClientError, DiscourseError,
                                    DiscourseRateLimitedError,
                                    DiscourseServerError)

from src.sources.models import Source

load_dotenv()

log = logging.getLogger("discourse.client")

api_username = (
    os.environ.get("DISCOURSE_API_USER")
    if os.environ.get("DISCOURSE_API_USER")
    else None
)
api_key = (
    os.environ.get("DISCOURSE_API_KEY") if os.environ.get("DISCOURSE_API_KEY") else None
)

client = DiscourseClient(
    os.environ.get("DISCOURSE_HOST"),
    api_username=api_username,
    api_key=api_key,
)


def _request(url):
    headers = {
        "Accept": "text/plain",
        "Api-Key": api_key,
        "Api-Username": api_username,
    }

    # How many times should we retry if rate limited
    retry_count = 4
    # Extra time (on top of that required by API) to wait on a retry.
    retry_backoff = 1

    while retry_count > 0:
        response = requests.get(url, headers=headers)

        log.debug("response %s: %s", response.status_code, repr(response.text))
        if response.ok:
            break
        if not response.ok:
            try:
                msg = ",".join(response.json()["errors"])
            except (ValueError, TypeError, KeyError):
                if response.reason:
                    msg = response.reason
                else:
                    msg = f"{response.status_code}: {response.text}"

            if 400 <= response.status_code < 500:
                if 429 == response.status_code:
                    # This codepath relies on wait_seconds from Discourse v2.0.0.beta3 / v1.9.3 or higher.
                    content_type = response.headers.get("Content-Type")
                    if content_type is not None and "application/json" in content_type:
                        ret = response.json()
                        wait_delay = (
                            retry_backoff + ret["extras"]["wait_seconds"]
                        )  # how long to back off for.
                    else:
                        # We got an early 429 error without a proper JSON body
                        ret = response.content
                        wait_delay = retry_backoff + 10

                    limit_name = response.headers.get(
                        "Discourse-Rate-Limit-Error-Code", "<unknown>"
                    )

                    log.info(
                        f"We have been rate limited (limit: {limit_name}) and will wait {wait_delay} seconds ({retry_count} retries left)",
                    )
                    if retry_count > 1:
                        time.sleep(wait_delay)
                    retry_count -= 1
                    log.debug(f"API returned {ret}")
                    continue
                else:
                    raise DiscourseClientError(msg, response=response)

            # Any other response.ok resulting in False
            raise DiscourseServerError(msg, response=response)

    if retry_count == 0:
        raise DiscourseRateLimitedError(
            "Number of rate limit retries exceeded. Increase retry_backoff or retry_count",
            response=response,
        )

    if response.status_code == 302:
        raise DiscourseError(
            "Unexpected Redirect, invalid api key or host?",
            response=response,
        )

    json_content = "application/json; charset=utf-8"
    content_type = response.headers["content-type"]
    if content_type == json_content:
        try:
            decoded = response.json()
        except ValueError as err:
            raise DiscourseError(
                "failed to decode response", response=response
            ) from err
    else:
        decoded = response.text

    return decoded


def _fetchTopicCentent(topic_id):
    url = f"{client.host}/raw/{topic_id}"
    return _request(url)


# add function to get the user's email address from their username
def _fetchTopics():
    site = client.get_site_info()
    categories = site["categories"]

    topics = []

    for category in categories:
        log.debug(f'Fetching {category["name"]} topics')
        category_topics = client.category_topics(category["id"])
        log.debug(f'  - {len(category_topics)} topics in {category["name"]}')
        for t in category_topics["topic_list"]["topics"]:
            url = f'{client.host}/t/{t["slug"]}/{t["id"]}'
            log.debug(f'  - {t["slug"]} ({url})')

            topic = client.topic(t["slug"], t["id"])
            content = _fetchTopicCentent(t["id"])
            content = f"#{topic["title"]}\n\n{content}"
            topic["content"] = content
            topic["category_name"] = category["name"]
            topic["category_slug"] = category["slug"]
            topic["url"] = url

            topics.append(topic)

    return topics


def getSources() -> List[Source]:
    sources = []
    # Get the topics
    topics = _fetchTopics()
    for topic in topics:
        meta = {"url": topic["url"], "title": topic["title"]}

        sources.append(
            Source(
                slug=f'discourse/{topic["slug"]}',
                content=topic["content"],
                meta=meta,
            )
        )

    return sources


if __name__ == "__main__":
    sources = getSources()
    print(f"Found {len(sources)} documents")
