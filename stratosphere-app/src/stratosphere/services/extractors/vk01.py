import json
from urllib.parse import parse_qs

from stratosphere.storage.models import Entity, Relationship
from stratosphere.stratosphere import Stratosphere, options
from stratosphere.utils.extractor_utils import DuplicateRows, decode, get_uuid_hash, json_loads, re_match
from stratosphere.utils.log import compact_exception_message, logger


def track_user(rows):
    # Look for friend lists
    for row in rows:
        if not (
            row.flow_request_method == "GET"
            and row.flow_request_url.startswith("https://vk.com/")
            and "text/html" in str(row.flow_response_headers_content_type)
            and "user_ids" in decode(row.flow_response_content)
        ):
            continue

        try:
            # In some cases, strings are escaped
            content = decode(row.flow_response_content).replace("\\", "")

            # Example for user_ids:
            user_ids = re_match('"user_ids":(.*?),', content, raise_exception=True)  # ["68870871']
            user_id = json.loads(user_ids)[0]  # '68870871'
            first_name = re_match(',"first_name_nom":"(.*?)"', content)  #
            last_name = re_match(',"last_name_ins":"(.*?)"', content)  #
            domain = re_match(',"domain":"(.*?)"', content)  #
            country = re_match(',"country":{.*?"title":"(.*?)"}', content)  # Russia
            city = re_match(',"city":{.*?"title":"(.*?)"}', content)  # Kursk
            bdate = re_match(',"bdate":"(.*?)"', content)  # 20.2
            skype = re_match(',"skype":"(.*?)"', content)  # -
            re_match("AvatarRich__background.*?img(.*?)/>", content)  # -
            full_name = f"{first_name} {last_name}"

            if "&_ref=id" in row.flow_request_url:
                prev_user_id = parse_qs(row.flow_request_url)["_ref"][0][2:]
            else:
                prev_user_id = None

        except Exception as e:  # noqa
            logger.info(
                f"Failed parsing vk.com person page for flow {row.flow_id} ({compact_exception_message(e)}), url:"
                f" {row.flow_request_url} request_content: {row.flow_request_content}"
            )
            continue

        # print(get_uuid_hash(user_id))

        s_kb = Stratosphere(options.get("db.url_kb"))
        dup_rows = DuplicateRows(s_kb.db)

        person1 = Entity(
            entity_id=get_uuid_hash(user_id),
            group="vk.com",
            type="person",
            data=json.dumps(
                {
                    "user_ids": user_ids,
                    "first_name": first_name,
                    "last_name": last_name,
                    "full_name": full_name,
                    "domain": domain,
                    "country": country,
                    "city": city,
                    "bdate": bdate,
                    "skype": skype,
                    "url_picture": None,
                }
            ),
            timestamp=row.flow_capture_timestamp,
        )

        # print(person.as_dict())

        dup_rows.add([person1])

        logger.info(f"Added entity {person1.entity_id} ({full_name})")

        if prev_user_id:
            person2 = Entity(
                entity_id=get_uuid_hash(prev_user_id),
                group="vk.com",
                type="person",
                data=json.dumps(
                    {
                        "user_ids": [get_uuid_hash(prev_user_id)],
                    }
                ),
                timestamp=row.flow_capture_timestamp,
            )

            rel = Relationship(
                relationship_id=get_uuid_hash(f"{person2.entity_id}-{person1.entity_id}"),
                group="vk.com",
                src=person2.entity_id,
                dst=person1.entity_id,
                type="friend",
                timestamp=row.flow_capture_timestamp,
            )
            dup_rows.add([rel])

            logger.info(f"Added relationship {person2.entity_id} -> {person1.entity_id}")

        dup_rows.merge_and_commit()


def track_friends(rows):
    s_kb = Stratosphere(options.get("db.url_kb"))
    dup_rows = DuplicateRows(s_kb.db)

    # Look for friend lists
    for row in rows:
        if not (
            row.flow_request_method == "POST"
            and row.flow_request_url.startswith("https://vk.com/al_friends.php")
            and "application/json" in str(row.flow_response_headers_content_type)
        ):
            continue

        try:
            # Let's parse the list of frends
            data = json_loads(row.flow_response_content)
            friends = data["payload"][1][0]["all"]
        except Exception as e:  # noqa
            logger.info(
                f"Failed parsing vk.com friends for flow {row.flow_id} ({compact_exception_message(e)}), url:"
                f" {row.flow_request_url} request_content: {row.flow_request_content}"
            )
            continue

        # ID of the person with friends.
        # Each user might have multiple IDs, we consider the 1st one to calculate the hash.
        src_user_ids = parse_qs(decode(row.flow_request_content))["id"]

        person1 = Entity(
            entity_id=get_uuid_hash(src_user_ids[0]),
            group="vk.com",
            type="person",
            data=json.dumps({"user_ids": json.dumps(src_user_ids)}),
            timestamp=row.flow_capture_timestamp,
        )

        dup_rows.add([person1])
        # session.merge(person1)
        logger.info(f"Added entity {person1.entity_id}")
        # print(person1.as_dict())

        for friend in friends:
            # ID of the friend
            # Each user might have multiple IDs, we consider the 1st one to calculate the hash.
            dst_user_ids = [str(friend[0])]

            person2 = Entity(
                entity_id=get_uuid_hash(dst_user_ids[0]),
                group="vk.com",
                type="person",
                data=json.dumps(
                    {
                        "user_ids": json.dumps(dst_user_ids),
                        "url_picture": friend[1],
                        "path": friend[2],
                        "full_name": friend[5],
                    }
                ),
                timestamp=row.flow_capture_timestamp,
            )

            dup_rows.add([person2])

            # logger.info(f"Added entity {person2.entity_id}")

            # print(person2.as_dict())

            rel = Relationship(
                relationship_id=get_uuid_hash(f"{src_user_ids[0]}-{dst_user_ids[0]}"),
                group="vk.com",
                src=person1.entity_id,
                dst=person2.entity_id,
                type="friend",
                timestamp=row.flow_capture_timestamp,
            )

            dup_rows.add([rel])
            # session.merge(rel)

            # logger.info(f"Added relationship {rel.relationship_id}")

        dup_rows.merge_and_commit()

        logger.info(f"Added {len(friends)} friends of entity {person1.entity_id}")


def extract(rows):
    track_friends(rows)
    track_user(rows)


extractor = {"name": "vk01", "func": extract}
