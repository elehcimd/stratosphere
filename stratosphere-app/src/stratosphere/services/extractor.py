import pkgutil
import time
from datetime import timedelta
from importlib import import_module, invalidate_caches

import stratosphere.extractors
from stratosphere.options import options
from stratosphere.storage.models import Flow, time_now
from stratosphere.stratosphere import Stratosphere
from stratosphere.utils.log import init_logging, logger


def get_list_extractors():
    # Extractors can be added at any time, and we'll pick them up.
    # In case new extractors are defined while the code is running, we need to invalidate
    # the  importlib cache, s.t. we can scan find also new modules.
    invalidate_caches()
    return [module_name for _, module_name, _ in pkgutil.iter_modules(stratosphere.extractors.__path__)]


def get_extractor_funcs():
    extractor_funcs = []
    for module_name in get_list_extractors():
        logger.info(f"Found extractor: {module_name}")
        m = import_module(f"stratosphere.extractors.{module_name}")
        extractor_funcs.append(m.extract)
    return extractor_funcs


class Extractor:
    def __init__(self, url_probe=None, url_kb=None):
        url_probe = url_probe or options.get("db.url_probe")
        url_kb = url_kb or options.get("db.url_kb")
        self.s_probe = Stratosphere(url_probe)
        self.s_kb = Stratosphere(url_kb)

    def process(self):
        logger.info("Processing new flows ...")
        extractor_funcs = get_extractor_funcs()
        logger.info("Querying probe ...")
        with self.s_probe.db.session() as session:
            rows = session.query(Flow).all()
        logger.info(f"Processing {len(rows)} flows ...")
        for extractor_func in extractor_funcs:
            try:
                extractor_func(rows, self.s_kb)
            except:  # noqa
                continue

    def prune(self):
        last_vacuum = None

        logger.info(f"Dropping expired flows (older than {options.get('extractors.expired_flows')}s)")
        with self.s_probe.db.session() as session:
            session.query(Flow).filter(
                Flow.flow_capture_timestamp <= time_now() - timedelta(seconds=options.get("extractors.expired_flows"))
            ).delete()
            session.commit()

        # Trigger VACUUM if:
        # probe file size larger than vacuum_size_trigger AND
        # last time triggered more than vacuum_min_delay seconds ago or first time
        if self.s_probe.db.size() > options.get("extractors.vacuum_size_trigger") and (
            last_vacuum is None
            or last_vacuum + timedelta(seconds=options.get("extractors.vacuum_min_delay")) <= time_now()
        ):
            logger.info("VACUUM ...")
            self.s_probe.db.vacuum()  # remove the records marked as deleted, freeing space.
            last_vacuum = time_now()
        logger.info(f"Waiting {options.get('extractors.loop_wait')}s")


def main():
    init_logging()
    logger.info("Extractor started")

    extractor = Extractor(url_probe=None, url_kb=None)

    while True:
        extractor.process()
        extractor.prune()
        time.sleep(options.get("extractors.loop_wait"))


if __name__ == "__main__":
    main()
