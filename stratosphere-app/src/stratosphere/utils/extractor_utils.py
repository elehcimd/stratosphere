import hashlib
import json
import re
import uuid

from stratosphere.storage.models import Entity, Relationship


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


def get_uuid_hash(data):
    return uuid.UUID(hex=hashlib.md5(f"{data}".encode()).hexdigest()).hex  # noqa


def re_match(pattern, content, raise_exception=False):
    if raise_exception:
        match = re.compile(pattern).search(content)[1]
        return match
    else:
        try:
            # print(re.compile(pattern).search(content)[0])
            match = re.compile(pattern).search(content)[1]
            return match
        except:  # noqa
            return None


class DuplicateRows:
    def __init__(self, db):
        self.db = db
        self.relationships = {}
        self.entities = {}

    def add(self, rows):
        for row in rows:
            if isinstance(row, Entity):
                if row.entity_id not in self.entities:
                    self.entities[row.entity_id] = [row]
                else:
                    self.entities[row.entity_id].append(row)
            else:
                if row.relationship_id not in self.relationships:
                    self.relationships[row.relationship_id] = [row]
                else:
                    self.relationships[row.relationship_id].append(row)
        return self

    def merge_and_commit(self):
        with self.db.session() as session:
            rows = session.query(Entity).filter(Entity.entity_id.in_(self.entities.keys())).all()
            self.add(rows)
            rows = session.query(Relationship).filter(Relationship.relationship_id.in_(self.relationships.keys())).all()
            self.add(rows)

        self.dedup_rows = []
        for _entity_id, rows in self.entities.items():
            # print(entity_id, len(rows))
            candidate = rows[0]
            candidate_data = json.loads(candidate.data) if candidate.data else {}

            for row in rows[1:]:
                data = json.loads(row.data) if row.data else {}
                candidate_data = {**candidate_data, **data}
            candidate.data = json.dumps(candidate_data)

            self.dedup_rows.append(candidate)

        for rows in self.relationships.values():
            candidate = rows[0]
            candidate_data = json.loads(candidate.data) if candidate.data else {}

            for row in rows[1:]:
                data = json.loads(row.data) if row.data else {}
                candidate_data = {**candidate_data, **data}
            candidate.data = json.dumps(candidate_data)

            self.dedup_rows.append(candidate)

        with self.db.session() as session:
            for row in self.dedup_rows:
                session.merge(row)
            session.commit()
