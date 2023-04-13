import os
import pkgutil
import time
from importlib import import_module, invalidate_caches
import stratosphere.extractors
from stratosphere.options import options
from stratosphere.storage.models import Flow, Entity, Relationship, func_time_now
from stratosphere.stratosphere import Stratosphere
from stratosphere.utils.log import init_logging, logger

from datetime import timedelta


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

        logger.info(f"Processing {len(rows)} flows ...")
        for extractor_func in extractor_funcs:
            try:
                extractor_func(rows)
            except:
                continue  # noqa


def main():
    init_logging()
    logger.info("Extractor started")

    extractor = Extractor()

    while True:
        logger.info("Processing new flows ...")
        extractor.process()
        logger.info(f"Dropping expired flows (older than {options.get('extractors.expired_flows')}s)")
        s_probe = Stratosphere(extractor.url)
        with s_probe.db.session() as session:
            session.query(Flow).filter(
                Flow.flow_capture_timestamp
                <= func_time_now() - timedelta(seconds=options.get("extractors.expired_flows"))
            ).delete()
            session.commit()
        # s_probe.db.vacuum()  # remove the records marked as deleted, freeing space.
        logger.info(f"Waiting {options.get('extractors.loop_wait')}s")
        time.sleep(options.get("extractors.loop_wait"))


if __name__ == "__main__":
    main()
