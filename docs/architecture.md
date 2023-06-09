#  **stratosphere** Architecture
The system relies on [mitmproxy](https://mitmproxy.org/) to intercept the web traffic (both desktop and mobile), building a knowledge base with [SQLite](https://sqlite.org/) that is later accessed by a suite of web apps built with [Jupyter](https://jupyter.org/) and [Voilà](https://voila.readthedocs.io/en/stable/). [supervisor](http://supervisord.org/) is used to manage the running services. The architecture is cross platform and runs locally inside a Docker container. The system includes these running services (entry points in `/shared/services/`):

* **mitmproxy**: running the HTTP/S proxy and adding the intercepted flows to `probe.db`.
* **extractor**: reading the flows from `probe.db`, adding entities and relationships to `kb.db`.
* **nginx**: proxying all services behind http://localhost:8082.
  * **jupterlab/Voilà**: JupyterLab server with Voilà extension to serve the web apps.
  * **sqliteweb**: Web-based SQLite database browser pointing to `kb.db`.

## Key Terms

### Knowledge Base

The knowledge base is stored as an SQlite database (`/shared/data/kb.db`) with two tables: `entities` and `relationships`. An entity describes a "thing", such as a web search result or an user. A relationship describes the connection between entities, such as a friendship between users.

#### Entities

Entities are uniquely identified by UUIDs that are generated by hashing their unique string identifiers. The definition of the unique string identifier is not fixed and it depends on the scraper that extracted it. For example, the entity of an user with ID `"123"` on social network `"xyz.com"` could be uniquely identified by the string `"xyz.com-123"`. Its UUID is defined by the 32-character hexadecimal string obtained from `UUID(hex=MD5("xyz.com-123"))`. The MD5 hashing algorithm, despite being cryptographically insecure, remains a sound choice in this context thanks to the length of its hashes (128 bits), that can be used with no further transformation as UUIDs. Each entity contains these attributes:

* `id`: UUID of the entity.
* `type`: Type of the entity, defined by extractor, always present. The current recommended format is `domain.name/typeofentity`. For example, `"google.com/search_query"` represents search results.
* `data`: JSON dictionary of properties. The schema depends on the type of entity and the available extracted data. If no data is available, the field is set to NULL.
* `blob`: Binary field, currently not used. It might be used to contain binary data such as images.
* `ts`: Timestamp of the captured flow (`flow.response.timestamp_start`).

The knowledge base contains always a NIL entity whose `id` column is seto to zeros (`"000..."`). NIL entities (and relationships) help simplify the code.

#### Relationships

Relationships are uniquely identified by the UUIDs obtained from hashing the concatenation of their UUIDs. Relationships might be directional. For example, the relationship between entities with UUIDs `"1.."` and `"2.."` is defined as `UUID(hex=MD5("1..2.."))`. Each entity contains these attributes:

* `id`: UUID of the relationship.
* `type`: Defined as in entities but applied to relationships.
* `src`: Source UUID of the relationship, always present.
* `dst`: Destination UUID of the relationship, always present.
* `data`: Defined as in entities but applied to relationships.
* `blob`: Defined as in entities but applied to relationships.
* `ts`: Defined as in entities but applied to relationships.

Similarly to the entities table, a NIL relationship is also always present, with  `id`, `src`, and `dst` columns are set to zeros.

#### On the importance of stable and robust UUIDs

The duty of the extractors is to process flows to insert new entities and relationships in the knowledge base.
If an entity is encountered several times, potentially on different web pages, a stable UUID lets us 
consolidate the knowledge in a unifying entity, merging the different data points.
Furthermore, UUIDs are the sole connection between entities and relationships.
For these reasons, it is critical to have a solid, robust design of the extraction of UUIDs for entities and relationships.