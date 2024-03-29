import json
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from stratosphere.storage.models import Entity, Relationship
from stratosphere.stratosphere import Stratosphere, options
from stratosphere.utils.extractor_utils import DuplicateRows, get_uuid_hash, get_uuid_pair_hash
from stratosphere.utils.log import compact_exception_message, logger


def extract(rows):
    s_kb = Stratosphere(options.get("db.url_kb"))
    dup_rows = DuplicateRows(s_kb.db)

    # Look for friend lists
    for row in rows:
        if not (
            row.flow_request_method == "GET"
            and row.flow_request_url.startswith("https://www.google.com/search")
            and "text/html" in str(row.flow_response_headers_content_type)
        ):
            continue

        try:
            query = parse_qs(urlparse(row.flow_request_url).query, keep_blank_values=True)

            search_string = query["q"][0].strip()

            urls = []

            soup = BeautifulSoup(row.flow_response_content, "html.parser")
            for a in soup.find_all("a", href=True):
                if not a["href"].startswith("htt") or "google.com" in a["href"]:
                    continue

                try:
                    # start with all the text we can render
                    text = a.text.strip()
                    # if there's none, look for alt tags
                    if len(text) == 0:
                        text = "\n".join([img["alt"] for img in a.find_all("img", alt=True)])
                    # finally, try to see if there's a title inside the text, prefer it if present
                    text = a.find("h3").text.strip()
                except:  # noqa
                    pass

                if len(text) == 0:
                    text = None

                urls.append({"url": a["href"], "text": text})
                # TODO: in some cases, there are duplicate URLs, and only one of them has a good description.
                # Right know, we end up retainining only the last one, as they all get merged.
                # print("Found the URL:", {"url": ["href"], "text": text})

        except Exception as e:  # noqa
            logger.info(f"Failed parsing google search results for flow {row.flow_id} ({compact_exception_message(e)})")
            continue

        entity1 = Entity(
            id=get_uuid_hash(search_string),
            type="google.com/search_query",
            data=json.dumps({"q": search_string}),
            ts=row.flow_capture_timestamp,
        )

        # print(entity.as_dict())

        dup_rows.add([entity1])

        for url in urls:
            entity2 = Entity(
                id=get_uuid_hash(f'{url["url"]}'),
                type="google.com/search_result",
                data=json.dumps(url),
                ts=row.flow_capture_timestamp,
            )
            # print(entity.as_dict())

            dup_rows.add([entity2])

            rel = Relationship(
                type="google.com/search_result",
                id=get_uuid_pair_hash(entity1.id, entity2.id),
                src=entity1.id,
                dst=entity2.id,
                data=json.dumps(url),
                ts=row.flow_capture_timestamp,
            )

            dup_rows.add([rel])

        logger.info(f'Added google search {entity1.id} ({len(urls)} results for query "{search_string}")')

        dup_rows.merge_and_commit()
