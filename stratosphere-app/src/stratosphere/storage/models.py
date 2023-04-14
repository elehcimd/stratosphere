import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, LargeBinary, String
from sqlalchemy.orm import declarative_base

# Construct a base class for declarative class definitions.
Base = declarative_base()

null_uuid = uuid.UUID(int=0).hex


def time_now():
    return datetime.now()


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
    flow_capture_timestamp = Column(DateTime, nullable=True, default=time_now)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Entity(Base):
    __tablename__ = "entities"
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    data = Column(String, nullable=True)
    blob = Column(LargeBinary, nullable=True, default=None)
    ts = Column(DateTime, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    src = Column(String, nullable=False)
    dst = Column(String, nullable=False)
    data = Column(String, nullable=True)
    blob = Column(LargeBinary, nullable=True, default=None)
    ts = Column(DateTime, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


null_entity = Entity(id=null_uuid, type="null", data=None, ts=time_now())
null_relationship = Relationship(id=null_uuid, src=null_uuid, dst=null_uuid, type="null", data=None, ts=time_now())
