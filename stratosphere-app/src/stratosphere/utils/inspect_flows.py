import json
import pandas as pd
from IPython.display import display
from urllib.parse import parse_qs, urlparse
from IPython.display import JSON


def pretty_print_dict(d, limit=None):
    text = json.dumps(d, indent=2)

    if limit:
        text = text[:limit]
    print(text)


def display_json_text(data, expanded=False):
    display(JSON(json_loads(data), expanded=expanded))


def decode(s, encodings=("ascii", "utf-8", "latin-1")):
    for encoding in encodings:
        try:
            return s.decode(encoding)
        except UnicodeDecodeError:
            pass
    return s.decode("ignore")


def json_loads(data):
    return json.loads(decode(data))


def is_json(data):
    try:
        json_loads(data)
        return True
    except (UnicodeDecodeError, json.decoder.JSONDecodeError):
        return False


from textwrap import wrap


class InspectFlow:
    def __init__(self, s):
        self.s = s

    def response_content_json(self):
        return json_loads(self.s.flow_response_content)

    def search(self, patterns=[], only_matches=False, is_json=True):
        s = self.s.copy()

        if is_json:
            text = json.dumps(json_loads(s.flow_response_content), indent=2).lower()
        else:
            text = "\n".join(wrap(decode(s.flow_response_content).lower(), width=130))

        patterns = [pattern.lower() for pattern in patterns]

        def process_line(idx, line, patterns):
            report = ""
            matches = set()
            for pattern in patterns:
                if pattern in line:
                    matches.add(pattern)

            if len(matches) > 0:
                report = f"Line {idx} matches for patterns {list(matches)}"

            text = f"[{'X' if len(matches) > 0 else ' '}] {idx:5}: {line}"
            if len(text) > 150:
                text = text[:150] + " [...]"
            return {"report": report, "text": text, "is_match": len(matches) > 0}

        lines = [process_line(idx, l, patterns) for idx, l in enumerate(text.splitlines())]

        # idx_matches = [line.idx for line in lines if line["is_match"]]

        if only_matches:
            text = "\n".join(line["text"] for line in lines if line["is_match"])
        else:
            text = "\n".join(line["text"] for line in lines)

        report = "\n".join(line["report"] for line in lines if len(line["report"]) > 0)

        print(report)
        print()
        print(text)

    def overview(self, response_content_expaned=False):
        s = self.s.copy()

        query = parse_qs(urlparse(s.flow_request_url).query, keep_blank_values=True)

        print("================================[URL]===========================================")
        print(f"METHOD: {self.s.flow_request_method}")
        print(f"URL: {self.s.flow_request_url}")
        print(f"Query:")
        display(JSON(query, expanded=True))
        print("================================[request-content]==============================")

        print(f"content-type: {s.flow_request_headers_content_type}")
        content_is_json = is_json(s.flow_request_content)
        print(f"JSON-parsable? {content_is_json}")
        if self.s.flow_request_method == "POST":
            print("--")
            if content_is_json:
                display_json_text(s.flow_request_content)
            elif "application/x-www-form-urlencoded" in s.flow_request_headers_content_type.lower():
                pretty_print_dict(parse_qs(decode(s.flow_request_content)))
            else:
                print(s.flow_request_content[:1000])
            print("--")
        print("================================[request-response]============================")
        print(f"content-type: {s.flow_response_headers_content_type}")
        content_is_json = is_json(s.flow_response_content)
        print(f"JSON-parsable? {content_is_json}")
        print("--")
        if content_is_json:
            display_json_text(s.flow_response_content, expanded=response_content_expaned)
        else:
            print(s.flow_response_content[:1000])
        print("--")


class InspectFlows:
    def __init__(self, df):
        self.df = df

    def overview(self):
        df = self.df.copy()
        df.flow_capture_timestamp = pd.to_datetime(df.flow_capture_timestamp)

        duration = (df.flow_capture_timestamp.max() - df.flow_capture_timestamp.min()).total_seconds()

        print(f"Overview: {len(df)} flows ({duration:.2f} seconds) distributed as follows:")

        df = (
            df[
                [
                    "flow_request_host",
                    "flow_request_port",
                    "flow_request_method",
                    "flow_request_headers_content_type",
                    "flow_response_headers_content_type",
                ]
            ]
            .value_counts(dropna=False)
            .reset_index()
        )
        df.columns = [
            "host",
            "port",
            "method",
            "flow_request_headers_content_type",
            "flow_response_headers_content_type",
            "count",
        ]
        display(df)

    def analyze(self, patterns=[]):
        df = self.df.copy()
        df.flow_capture_timestamp = pd.to_datetime(df.flow_capture_timestamp)
        # scheme://netloc/path;parameters?query#fragment
        df["url_path"] = df.flow_request_url.apply(lambda url: urlparse(url).path)
        df["url_path_beginswith"] = df["url_path"].str[:30]
        df["url_params"] = df.flow_request_url.apply(lambda url: urlparse(url).params)
        df["url_query"] = df.flow_request_url.apply(lambda url: urlparse(url).query)
        df["url_fragment"] = df.flow_request_url.apply(lambda url: urlparse(url).fragment)
        df["response_is_text"] = df.flow_response_headers_content_type.astype(str).apply(
            lambda s: any([pattern in s.lower() for pattern in ["text", "charset=", "utf-8", "json"]])
        )

        df["response_is_json"] = df.flow_response_content.apply(is_json)
        df["host_port_method"] = df.apply(
            lambda row: f"{row.flow_request_host}:{row.flow_request_port}@{row.flow_request_method}", axis=1
        )

        df["flow_response_content_startswith"] = df["flow_response_content"].str[:30]

        df = df[df.response_is_text]

        cols = [
            "flow_capture_timestamp",
            "host_port_method",
            "url_path_beginswith",
            "response_is_text",
            "response_is_json",
            "flow_response_content_startswith",
        ]

        if len(patterns) > 0:
            df["n_matches"] = df.flow_response_content.astype(str).apply(
                lambda s: sum([int(pattern.lower() in s.lower()) for pattern in patterns])
            )
            df = df[df.n_matches > 0]
            cols.append("n_matches")

        df = df[cols]

        return df

    def flow(self, idx):
        return InspectFlow(self.df.loc[idx])
