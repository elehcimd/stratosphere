import json
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from stratosphere.storage.models import Entity, Relationship
from stratosphere.stratosphere import Stratosphere, options
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
    s_kb = Stratosphere(options.get("db.url_kb"))
    dup_rows = DuplicateRows(s_kb.db)

    # Look for friend lists
    for row in rows:
        if not (
            row.flow_request_method == "GET"
            and row.flow_request_url.startswith("https://www.linkedin.com/voyager/api/graphql")
            # and "text/json" in str(row.flow_response_headers_content_type)
        ):
            continue

        try:


            # the connection relation is hidden in the URL -> ACoAAAAFpxEBmgCXnT_YjkXzd7NZS8RWQV_lJbY
            # https://www.linkedin.com/voyager/api/graphql?variables=(start:0,origin:SHARED_CONNECTIONS_CANNED_SEARCH,query:(flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:connectionOf,value:List(ACoAAAAFpxEBmgCXnT_YjkXzd7NZS8RWQV_lJbY)),(key:network,value:List(F)),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.181547298141ca2c72182b748713641b


            query = parse_qs(urlparse(row.flow_request_url).query, keep_blank_values=True)

            # search_string = query["q"][0].strip()






            content = decode(row.flow_response_content).replace("\\", "")

            json_object = json.loads(content)

            # logger.info(json_object['included'])


            included_data = json_object['included']


            for data_part in included_data:

                if ( 'template' in data_part and 'trackingUrn' in data_part):

                    if not (data_part['trackingUrn'] == None):


                        # logger.info(data_part)

                        # get the user hash of the shaerd contact
                        logger.info(query['variables'][0].strip())


                        s = query['variables'][0].strip()
                        following_user_hash = s.split(',value:List(')[1].split('))')[0]

                        logger.info(following_user_hash)


                        ##########3


                        # following_user_hash is the linkedin hash id of the user id everybody is following

                        # at this point we would need to look this up in our DB


                        ############



                        
                        urnParts = data_part['trackingUrn'].split(":") #'trackingUrn': 'urn:li:member:123456'
                        user_id = urnParts[-1]

                        logger.info(user_id)





                        logger.info(data_part['title']['text'])




                        
                        # profile url
                        logger.info(data_part['navigationUrl'])
                        urlParts = data_part['navigationUrl'].split("?") #'objectUrn': 'urn:li:member:123456'
                        logger.info(urlParts[0])

                        profile_url = urlParts[0]



                        #get the public_identifier (last part of the url)
                        public_identifier_parts = profile_url.split("/")
                        public_identifier = public_identifier_parts[-1]

                        logger.info(public_identifier)


                        # headline

                        logger.info(data_part['primarySubtitle']['text'])



                        #get the user hash ->*profile

                        user_hash_urn = data_part['image']['attributes'][0]['detailData']['nonEntityProfilePicture']['*profile'].split(":")
                        user_hash = user_hash_urn[-1]
                        logger.info(user_hash)





                        # get the image

                        logger.info(data_part['image']['attributes'][0]['detailData']['nonEntityProfilePicture']['vectorImage']['artifacts'][0]['fileIdentifyingUrlPathSegment'])

                        



                        first_name = 'None'
                        last_name = 'None'
                        occupation = 'None'
                        postal_code = 'None'
                        profile_picture = None





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


                        # rel = Relationship(
                        #     id=get_uuid_pair_hash(user_id, company_id),
                        #     type="linkedin.com/company",
                        #     src=get_uuid_hash(user_id),
                        #     dst=company.id,
                        #     ts=row.flow_capture_timestamp,
                        # )

                        # dup_rows.add([rel])

                        # dup_rows.merge_and_commit()
                
        except Exception as e:  # noqa
            logger.info(
                f"Failed parsing linkedin.com search results for flow {row.flow_id} ({compact_exception_message(e)}), url:"
                f" {row.flow_request_url} request_content: {row.flow_request_content}"
            )
            continue

        

        
