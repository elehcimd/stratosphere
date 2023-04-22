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
            and row.flow_request_url.startswith("https://www.linkedin.com/voyager/api/identity/dash/pro")
            # and "text/json" in str(row.flow_response_headers_content_type)
        ):
            continue

        try:
            content = decode(row.flow_response_content).replace("\\", "")

            json_object = json.loads(content)

            # logger.info(json_object['included'])


            included_data = json_object['included']


            for data_part in included_data:

                

                # companyName

                # find the profile user hash by checking 'entityUrn': 'urn:li:fsd_profile:ACoAAB8rG_UB7cstjC__gk5318uYsZOIVkyysi4'
                # if company is found create/update the company and relation to the user


                if ( 'entityUrn' in data_part and 'companyName' in data_part):
                    logger.info(data_part['companyName'])
                    logger.info(data_part['companyUrn'])

                    if not (data_part['companyUrn'] == None):
                        logger.info('Public Company')
                        
                        urnParts = data_part['companyUrn'].split(":") #'objectUrn': 'urn:li:member:123456'
                        logger.info(urnParts[-1])

                        company_id = urnParts[-1]


                        logger.info(data_part['$anti_abuse_metadata']['/companyUrn']['sourceUrns']['com.linkedin.common.urn.MemberUrn'])

                        companyUrnParts = data_part['$anti_abuse_metadata']['/companyUrn']['sourceUrns']['com.linkedin.common.urn.MemberUrn'].split(":") #'objectUrn': 'urn:li:member:123456'
                        logger.info(companyUrnParts[-1])

                        user_id = companyUrnParts[-1]

                        # user_id = data_part['$anti_abuse_metadata']

                        # company = Entity(
                        #     id=get_uuid_hash(dst_user_ids[0]),
                        #     type="linkedin.com/company",
                        #     data=json.dumps(
                        #         {
                        #             "user_ids": json.dumps(dst_user_ids),
                        #             "url_picture": friend[1],
                        #             "path": friend[2],
                        #             "full_name": friend[5],
                        #         }
                        #     ),
                        #     ts=row.flow_capture_timestamp,
                        # )

                        # dup_rows.add([company])

                        # rel = Relationship(
                        #     id=get_uuid_pair_hash(person1.id, company.id),
                        #     type="linkedin.com/company",
                        #     src=get_uuid_hash(user_id),
                        #     dst=company.id,
                        #     ts=row.flow_capture_timestamp,
                        # )

                        # dup_rows.add([rel])

                        # dup_rows.merge_and_commit()
                
        except Exception as e:  # noqa
            logger.info(
                f"Failed parsing linkedin.com person page for flow {row.flow_id} ({compact_exception_message(e)}), url:"
                f" {row.flow_request_url} request_content: {row.flow_request_content}"
            )
            continue

        

        
