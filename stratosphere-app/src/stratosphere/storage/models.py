from stratosphere.options import options
from sqlalchemy import Integer, BigInteger, Column, LargeBinary, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils.types.uuid import UUIDType
from datetime import datetime
import uuid

# Construct a base class for declarative class definitions.
Base = declarative_base()

# UUID type, to be used in model definitions. By passing binary=False, we fall back
# to the string representation of UUIDs if there's no native type (as in SQLite).
uuid_type = UUIDType(binary=False)


class Flow(Base):
    # https://docs.mitmproxy.org/stable/api/mitmproxy/flow.html
    # https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response
    """Model representing a request,response pair."""
    __tablename__ = "flows"
    flow_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    flow_index = Column(Integer, nullable=False, default=0)
    flow_request_host = Column(String, nullable=False)
    flow_request_port = Column(Integer, nullable=False)
    flow_request_method = Column(String, nullable=False)
    flow_request_pretty_url = Column(String, nullable=False)
    flow_request_url = Column(String, nullable=False)
    flow_request_http_version = Column(String, nullable=False)
    flow_request_headers = Column(String, nullable=False)
    flow_request_headers_content_type = Column(String, nullable=True)
    flow_request_content = Column(LargeBinary, nullable=True)
    flow_request_timestamp_start = Column(DateTime, nullable=False)
    flow_response_status_code = Column(Integer, nullable=False)
    flow_response_http_version = Column(String, nullable=False)
    flow_response_headers = Column(String, nullable=False)
    flow_response_headers_content_type = Column(String, nullable=True)
    flow_response_content = Column(LargeBinary, nullable=True)
    flow_response_timestamp_start = Column(DateTime, nullable=False)
    flow_capture_timestamp = Column(DateTime, nullable=True, default=lambda: datetime.now())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Entity(Base):
    __tablename__ = "entities"

    entity_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(String, nullable=True)
    blob = Column(LargeBinary, nullable=True, default=None)
    timestamp = Column(DateTime, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Relationship(Base):
    __tablename__ = "relationships"

    relationship_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group = Column(String, nullable=False)
    type = Column(String, nullable=False)
    src = Column(uuid_type, nullable=False)
    dst = Column(uuid_type, nullable=False)
    data = Column(String, nullable=True)
    blob = Column(LargeBinary, nullable=True, default=None)
    timestamp = Column(DateTime, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
