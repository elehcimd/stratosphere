from stratosphere import options
from stratosphere.storage.database import Database
from stratosphere.storage.models import Flow
from stratosphere.utils.log import init_logging, logger


class Stratosphere:
    def __init__(self, url: str = None):
        init_logging()

        if url is None:
            url = options.get("db.url")

        self.db = Database(url)

    def delete_all(self):
        with self.db.session() as session:
            session.query(Flow).delete()
            session.commit()
            self.db.vacuum()

    def capture(self, url: str = None, query_df: bool = True):
        from datetime import datetime

        logger.info("Starting flows capture")
        sample_start = datetime.now()
        input("Enter to complete ....")
        sample_end = datetime.now()

        with self.db.session() as session:
            rows = (
                session.query(Flow)
                .filter(
                    Flow.flow_request_timestamp_start >= sample_start, Flow.flow_response_timestamp_start <= sample_end
                )
                .all()
            )

        s = Stratosphere(url)

        logger.info(f"Captured {len(rows)} flows")

        # Delete all existing flows from prior captures
        with s.db.session() as session:
            session.query(Flow).delete()
            session.commit()
        s.db.vacuum()

        with s.db.session() as session:
            for row in rows:
                # https://stackoverflow.com/questions/45802620/copying-data-from-one-sqlalchemy-session-to-another
                session.merge(row)
            session.commit()

        if query_df:
            return s.db.pandas("select * from flows order by flow_capture_timestamp asc")
