import time

from stratosphere.utils.log import logger, init_logging
from stratosphere.options import options
from stratosphere.stratosphere import Stratosphere
from stratosphere.storage.models import Flow

from stratosphere.services.extractors.vk01 import extractor as extractor_vk01
from stratosphere.services.extractors.search_google import extractor as extractor_search_google
from stratosphere.services.extractors.dummy import extractor as dummy_extract

import os


class Extractor:
    def __init__(self, url=None):
        if url is None:
            url = options.get("db.url_probe")

        self.url = url

        self.s_kb = Stratosphere(options.get("db.url_kb"))

        self.extractors = {}
        self.register_extractor(dummy_extract)
        self.register_extractor(extractor_vk01)
        self.register_extractor(extractor_search_google)

    def register_extractor(self, extractor_desc):
        self.extractors[extractor_desc["name"]] = extractor_desc["func"]

    def process(self):
        self.s_probe = Stratosphere(self.url)

        with self.s_probe.db.session() as session:
            rows = session.query(Flow).all()
        logger.info(f"Processing {len(rows)} flows: start")

        for extractor_func in self.extractors.values():
            extractor_func(rows)
        logger.info(f"Processing {len(rows)} flows: end")


def main():
    init_logging()
    logger.info("Extractor started")

    extractor = Extractor()

    while True:
        logger.info("Processing new flows ...")
        extractor.process()

        # we might miss some flows here, if the probe writes to the file handler and we remove it
        # before processing them.

        # logger.info("Removing old flows ...")
        try:
            pass
            os.remove("/shared/data/probe.db")
        except OSError:
            pass

        # logger.info("Waiting for more flows ...")
        time.sleep(10)


if __name__ == "__main__":
    main()
