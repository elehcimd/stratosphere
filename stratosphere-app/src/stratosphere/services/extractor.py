import os
import pkgutil
import time
from importlib import import_module, invalidate_caches

import stratosphere.extractors
from stratosphere.options import options
from stratosphere.storage.models import Flow
from stratosphere.stratosphere import Stratosphere
from stratosphere.utils.log import init_logging, logger


class Extractor:
    def __init__(self, url=None):
        if url is None:
            url = options.get("db.url_probe")
        self.url = url

        invalidate_caches()
        self.extractor_funcs = []
        for _, module_name, _ in pkgutil.iter_modules(stratosphere.extractors.__path__):
            logger.info(f"Registering extractor: {module_name}")
            m = import_module(f"stratosphere.extractors.{module_name}")
            self.extractor_funcs.append(m.extract)

    def process(self):
        self.s_probe = Stratosphere(self.url)

        with self.s_probe.db.session() as session:
            rows = session.query(Flow).all()
        logger.info(f"Processing {len(rows)} flows: start")
        for extractor_func in self.extractor_funcs:
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
