import datetime
import json
import re

from stratosphere import Stratosphere
from stratosphere.storage.models import Flow
from stratosphere.utils.log import init_logging, logger

init_logging()


# https://docs.mitmproxy.org/stable/addons-examples/#nonblocking
async def response(flow):
    response_content_type = flow.response.headers.get("content-type")
    response_content_type_str = str(response_content_type)

    logger.info(f"response_content_type: {response_content_type_str}")

    if (
        "text" not in response_content_type_str
        and "html" not in response_content_type_str
        and "json" not in response_content_type_str
        and "utf-8" not in response_content_type_str
    ):
        return

    while True:
        try:
            stratosphere = Stratosphere("sqlite:////shared/data/probe.db")
            with stratosphere.db.session() as session:
                record = Flow(
                    flow_request_host=flow.request.host,
                    flow_request_port=flow.request.port,
                    flow_request_method=flow.request.method,
                    flow_request_pretty_url=flow.request.pretty_url,
                    flow_request_url=flow.request.url,
                    flow_request_http_version=flow.request.http_version,
                    flow_request_headers=json.dumps(dict(flow.request.headers.items())),
                    flow_request_headers_content_type=flow.request.headers.get("content-type"),
                    flow_request_content=flow.request.content,
                    flow_request_timestamp_start=datetime.datetime.fromtimestamp(flow.request.timestamp_start),
                    flow_response_status_code=flow.response.status_code,
                    flow_response_http_version=flow.response.http_version,
                    flow_response_headers=json.dumps(dict(flow.response.headers.items())),
                    flow_response_headers_content_type=flow.response.headers.get("content-type"),
                    flow_response_content=flow.response.content,
                    flow_response_timestamp_start=datetime.datetime.fromtimestamp(flow.response.timestamp_start),
                )
                session.add(record)
                session.commit()
        except:  # noqa
            # It might happen that the extractor just dropped the file ...
            # this causes an error (table not found, ...). We try again.
            continue
        break

    if flow.response and flow.response.content and "html" in response_content_type_str:
        # https://github.com/ondrakrat/js-mitm-proxy/blob/master/src/inject_script.py
        # delete CORS header if present
        # if "Content-Security-Policy" in flow.response.headers:
        #    del flow.response.headers["Content-Security-Policy"]

        # print(flow.request.url)

        # Look for body, and inject a div on top. The rest of the document is embedded in a 2nd div
        # to ensure that the 1st one remains visible.
        match = re.compile(b"<body(.*?)>").search(flow.response.content)
        if match:
            flow.response.content = (
                flow.response.content[: match.end()]
                + b'<div style="display: table; padding:2px; position: fixed;top:0;left:0;z-index:999;'
                + b"height:15px;font-size:15px;color:black;background-color:white;border: 1px solid black;"
                b' text-decoration: none;">'
                + b'<a target="_blank"'
                b' href="http://localhost:8082/jupyter/voila/render/webapps/index.ipynb"><b>S</b></a>'
                + b'</div><div style="top:15;left:0;z-index:998;">'
                + flow.response.content[match.end() :]
                + b"</div>"
            )
