import json
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from stratosphere.storage.models import Entity, Relationship
from stratosphere.stratosphere import Stratosphere, options
<<<<<<< HEAD
from stratosphere.utils.extractor_utils import (
    DuplicateRows,
    decode,
    get_uuid_hash,
    get_uuid_pair_hash,
    json_loads,
    is_json,
    re_match,
)

from stratosphere.utils.log import compact_exception_message, logger


# geoLocation -> postalCode
# objectUrn: 'urn:li:member:123456'
# entityUrn: 'urn:li:fsd_profile:ACoDDDERFGdsaoekV_ApllIvtEWEqeD1UVU'
# influencer: True:False
# premium: true:False


def extract(rows):
=======
from stratosphere.utils.extractor_utils import DuplicateRows, get_uuid_hash, get_uuid_pair_hash
from stratosphere.utils.log import compact_exception_message, logger


def extract(rows, s_kb):
>>>>>>> c800dbe (rev)
    s_kb = Stratosphere(options.get("db.url_kb"))
    dup_rows = DuplicateRows(s_kb.db)

    # Look for friend lists
<<<<<<< HEAD
    for row in rows:
        if not (
            row.flow_request_method == "GET"
            and row.flow_request_url.startswith("https://www.linkedin.com/in/")
            and "text/html" in str(row.flow_response_headers_content_type)
        ):
            continue
=======

    for row in rows:
        if not (
            row.flow_request_method == "GET"
            and row.flow_request_url.startswith("https://www.linkedin.com/voyager/api/graphql")
            and "charset=UTF-8" in str(row.flow_response_headers_content_type)
        ):
            continue
        logger.info(row.flow_request_url)
>>>>>>> c800dbe (rev)

        try:
            query = parse_qs(urlparse(row.flow_request_url).query, keep_blank_values=True)

<<<<<<< HEAD
            soup = BeautifulSoup(row.flow_response_content, "html.parser")

            for code_element in soup.find_all("code", id=True):
                #logger.info(f"found code element {code_element.text} ")
                if not (
                    "anti_abuse_metadata" in code_element.text
                    and "defaultLocalizedNameWithoutCountryName" in code_element.text
                ):
                    continue

                try:

                    text = code_element.text.strip()

                    # logger.info(f"found code element {text} ")

                    content = json.loads(text)

                    # logger.info(content['data'])
                    # logger.info(content['meta'])
                    # logger.info(content['included'][0])
                    # logger.info(content)

                    occupation = 'None'
                    postal_code = 'None'
                    profile_picture = None

                    for data_part in content['included']:

                        # fsd_profileCard
                        if not (
                            "fsd_profileCard" in str(data_part) 
                            or "countryUrn" in str(data_part)
                        ):
                            continue

                        try:

                            # logger.info(data_part)


                            if ( 'objectUrn' in data_part and 'birthDateOn' in data_part):
                                # logger.info(data_part['objectUrn'])
                                urnParts = data_part['objectUrn'].split(":") #'objectUrn': 'urn:li:member:123456'
                                logger.info(urnParts[-1])

                                user_id = urnParts[-1]

                            if ( 'entityUrn' in data_part and 'birthDateOn' in data_part):
                                # logger.info(data_part['entityUrn'])

                                urnParts = data_part['entityUrn'].split(":") # 'entityUrn': 'urn:li:fsd_profile:ACoAAABJxxxxxxxxxV_ApllIvtExxxxxxUVU'
                                logger.info(urnParts[-1])

                                user_hash = urnParts[-1]

                            if 'publicIdentifier' in data_part:
                                logger.info(data_part['publicIdentifier'])
                                public_id = data_part['publicIdentifier']

                            if 'firstName' in data_part:
                                logger.info(data_part['firstName'])
                                first_name = data_part['firstName']

                            if 'lastName' in data_part:
                                logger.info(data_part['lastName'])
                                last_name = data_part['lastName']
                                full_name = f"{first_name} {last_name}"
                            
                            if 'headline' in data_part:
                                logger.info(data_part['headline'])
                                headline = data_part['headline']

                            if 'occupation' in data_part:
                                logger.info(data_part['occupation'])
                                occupation = data_part['occupation']

                            if 'birthDateOn' in data_part:
                                logger.info(data_part['birthDateOn'])
                                bdate = data_part['birthDateOn']


                            if 'profilePicture' in data_part:
                                logger.info(data_part['profilePicture']['displayImageReference']['vectorImage']['rootUrl'])
                                logger.info(data_part['profilePicture']['displayImageReference']['vectorImage']['artifacts'][3]['fileIdentifyingUrlPathSegment'])

                                rootUrl = data_part['profilePicture']['displayImageReference']['vectorImage']['rootUrl']
                                fileIdentifyingUrlPathSegment = data_part['profilePicture']['displayImageReference']['vectorImage']['artifacts'][3]['fileIdentifyingUrlPathSegment']
                                profile_picture = rootUrl + fileIdentifyingUrlPathSegment

                            if 'postalCode' in str(data_part):
                                logger.info(data_part['geoLocation']['postalCode'])
                                postal_code = data_part['geoLocation']['postalCode']

                            if 'defaultLocalizedName' in data_part:
                                logger.info(data_part['defaultLocalizedName'])
                                country = data_part['defaultLocalizedName']

                            if 'defaultLocalizedNameWithoutCountryName' in data_part:
                                logger.info(data_part['defaultLocalizedNameWithoutCountryName'])
                                city = data_part['defaultLocalizedNameWithoutCountryName']


                            # logger.info(user_id)


                        except Exception as e:  # noqa
                            logger.info(
                                f"Failed parsing linkedin.com person datapart for flow {row.flow_id} ({compact_exception_message(e)}), url:"
                                f" content: {str(data_part)}"
                            )
                            continue



                except:  # noqa
                    pass

                
        except Exception as e:  # noqa
            logger.info(
                f"Failed parsing linkedin.com person page for flow {row.flow_id} ({compact_exception_message(e)}), url:"
                f" {row.flow_request_url} request_content: {row.flow_request_content}"
            )
            continue

        logger.info(f" user_id: {user_id}")

        person1 = Entity(
            id=get_uuid_hash(user_id),
            type="linkedin.com/person",
            data=json.dumps(
                {
                    "user_id": user_id,
                    "user_hash": user_hash,
                    "public_identifier": public_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "full_name": full_name,
                    "occupation": occupation,
                    "headline": headline,
                    "country": country,
                    "city": city,
                    "postal_code": postal_code,
                    "bdate": bdate,
                    "url_picture": profile_picture,
                }
            ),
            ts=row.flow_capture_timestamp,
        )

        logger.info(person1.as_dict())

        dup_rows.add([person1])

        print(f"Added entity {person1.id} ({full_name})")

        

        dup_rows.merge_and_commit()
=======
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
>>>>>>> c800dbe (rev)
