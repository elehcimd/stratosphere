import os
import pkgutil
import time
from importlib import import_module, invalidate_caches

import stratosphere.extractors
from stratosphere.options import options
from stratosphere.storage.models import Flow, Entity, Relationship
from stratosphere.stratosphere import Stratosphere
from stratosphere.utils.log import init_logging, logger


class Extractor:
    def __init__(self, url=None):
        if url is None:
            url = options.get("db.url_probe")
        self.url = url

    def process(self):
        # Extractors can be added at any time, and we'll pick them up.
        # In case new extractors are defined while the code is running, we need to invalidate
        # the  importlib cache, s.t. we can scan find also new modules.
        invalidate_caches()
        extractor_funcs = []
        for _, module_name, _ in pkgutil.iter_modules(stratosphere.extractors.__path__):
            logger.info(f"Found extractor: {module_name}")
            m = import_module(f"stratosphere.extractors.{module_name}")
            extractor_funcs.append(m.extract)

        s_probe = Stratosphere(self.url)

        # Drop entities and relationships tables: they're always empty
        #  and if their schema changes, we shouldn't worry here.
        # Entity.__table__.drop(s_probe.db.engine)
        # Relationship.__table__.drop(s_probe.db.engine)

        with s_probe.db.session() as session:
            rows = session.query(Flow).all()
        logger.info(f"Processing {len(rows)} flows: start")
        for extractor_func in extractor_funcs:
            extractor_func(rows)
        logger.info(f"Processing {len(rows)} flows: end")


def main():
    init_logging()
    logger.info("Extractor started")

    extractor = Extractor()

    while True:
        logger.info("Processing new flows ...")
        extractor.process()

        # TODO
        # We drop the processed flows.
        # Ideally, we drop only the ones we processed, to avoid
        # race conditions that might result in missed tracked flows.
        s_probe = Stratosphere(extractor.url)
        Flow.__table__.drop(s_probe.db.engine)

        time.sleep(10)


if __name__ == "__main__":
    main()
