from datetime import datetime

from stratosphere.storage.models import Entity, Relationship
from stratosphere.stratosphere import Stratosphere, options
from stratosphere.utils.extractor_utils import DuplicateRows, get_uuid_hash

dummy_uuid = get_uuid_hash("dummy")


def add_dummy(rows=None):
    s_kb = Stratosphere(options.get("db.url_kb"))
    dup_rows = DuplicateRows(s_kb.db)

    entity1 = Entity(
        entity_id=dummy_uuid,
        group="dummy",
        type="dummy",
        data="{}",
        timestamp=datetime.now(),
    )
    rel = Relationship(
        group="dummy",
        type="dummy",
        relationship_id=dummy_uuid,
        src=entity1.entity_id,
        dst=entity1.entity_id,
        data="{}",
        timestamp=datetime.now(),
    )

    dup_rows.add([entity1, rel])

    # logger.info(f"Added dummy entity ({entity1.entity_id}) and relationship {rel.relationship_id}")

    dup_rows.merge_and_commit()


def extract(rows):
    add_dummy(rows)


extractor = {"name": "dmmy", "func": extract}
