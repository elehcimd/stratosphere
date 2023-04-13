# The **stratosphere** project

**stratosphere** is a free and open source OSINT platform that automatically collects every page you visit, building a private knowledge base you can analyze with Jupyter notebooks and an extensible suite of web apps including:

* **Google sarch results**: Review your past Google search results
* **vk.com contacts explorer**: Explore previously seen vk.com contacts, highlighting their connections
* **Entity overview**: Navigat

You can also use the platform to quickly reverse-engineer HTTP/HTTPS web requests, including REST APIs. This lets you unlock the potential of private REST APIs, investigate GDPR breaches, and implement new scrapers to extend the knowledge base and power new web apps.

## Getting started

### 1. Install Docker

Docker is a tool that is used to automate the deployment of applications in lightweight containers so that
applications can work efficiently in different environments.
You can follow the [official installation instructions](https://docs.docker.com/get-docker/).

### 2. Pull the image and start the container

You can now download and run the image.
Execute from the command line:

```
docker pull micheda/stratosphere-app:latest
```

```
docker run --rm --name stratosphere-app -p 8080:8080 -p 127.0.0.1:8082:8082 \
  micheda/stratosphere-app:latest
```

After executing the last command, the container is running in foreground, 
with all services reporting a `successful` status.
If you want to interrupt the execution, simply press `ctrl-c` or `cmd-c`.

### 3. Configure your browser or device

You need to configure your browser or device to route all traffic through the HTTP proxy listening on:

```
http://localhost:8080
```

Browser versions and configurations frequently change, you should search the web on how to configure an HTTP proxy for your system.
Some operating systems have a global settings, some browsers have their own, other applications use environment variables, etc.

I recommend FoxyProxy, a browser extension that let you quickly switch between different proxy settings:

* [Firefox](https://addons.mozilla.org/it/firefox/addon/foxyproxy-standard/)
* [Chrome, Brave](https://chrome.google.com/webstore/detail/foxyproxy-standard/gcknhkkoolaabfmlnjonogaaifnjlfnp?hl=it)

#### Install the mitmproxy Certificate Authority

You can check that your web traffic is going through mitmproxy by browsing to http://mitm.it.
It should present you with a simple page to install the mitmproxy Certificate Authority, which is also the next step.
Follow the instructions for your OS / system and install the CA.

### 4. Test the web tracking

You can test that the system is working properly by browsing to https://www.google.com and verifying the presence of
a banner `[S]` on the top left corner of the page. Congratulations! **Stratosphere** is up and working properly.
The banner is always visible on all tracked pages. If missing, try refreshing the page with `ctrl-r`.

You can now access the dashboard by clicking on it or browsing to [http://localhost:8082](http://localhost:8082).

You will see the message `WARNING: No mounted volume detected on /shared`, informing you
that the newly captured information, analyses, and any other modification is lost once the Docker container is terminated.
If you want to persist the data, you can follow the next optional step.

### 5. How to persist the data

You can persist your changes (including the knowledge base, analyses, custom extractors and analyses) by 
mounting the `stratosphere-app` directory of this repository on the `/shared` mount point in the container.

Firstly, clone this repository and verify the absolute path of the directory you want to mount:

```
git clone https://github.com/elehcimd/stratosphere.git
cd stratosphere/stratosphere-app
pwd
```

Assuming that the absolute path to the directory is `/xyz/stratosphere-app`, 
execute from the command line:

```
docker run -d --rm --name stratosphere-app -p 8080:8080 -p 127.0.0.1:8082:8082 \
  -v /xyz/stratosphere-app:/shared micheda/stratosphere-app:latest
```

On Windows, the host path (before `:`) must be a valid Windows path (meaning: it starts with `C://....`).
The additional parameter `-v` takes care of mounting the volume, `-d` runs the container in background.

An overview of useful Docker parameters:

* [--rm](https://docs.docker.com/engine/reference/run/#clean-up---rm): Docker will automatically clean up the container and remove the file system when the container exits. If you want to retain the container’s file system, remove `--rm`.
* [-p](https://docs.docker.com/engine/reference/run/#expose-incoming-ports): Publish the container's port on the host. The format is `host_ip:host_port:container_port`. If you drop the `host_ip`, the port will be published on all interfaces. By default, the proxy runs on all intefaces, but the web interface is accessible only from localhost.
* [--name](https://docs.docker.com/engine/reference/run/#name---name): Name your container. 
* [-d](https://docs.docker.com/engine/reference/run/#detached-vs-foreground): Start the container in background.
* [-it](https://docs.docker.com/engine/reference/run/#foreground): Allocate a pseudo-tty and keep STDIN open even if not attached. Useful if you want to access directly the container from terminal, via `docker execute`.
* [-v](https://docs.docker.com/engine/reference/run/#volume-shared-filesystems): Bind mount a volume.

## Core concepts

### The knowledge base

The knowledge base is stored as an SQlite database (`/shared/data/kb.db`) with two tables: `entities` and `relationships`. An entity describes a "thing", such as a web search result or an user. A relationship describes the connenction between entities, such as a friendship between users.

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

### How to create new Jupyter notebooks and Voilà web apps

You can access JupyterLab from the main dashboard. The notebooks located in the subdirectory `webapps` are also published as Voilà web applications.

The example notebook `01 kb overview.ipynb` shows how to query the knowledge base with SQL and Pandas. The `stratosphere` Python package is included directly from source extending the `PYTHONPATH` env variable and it is located at `/shared/src/stratosphere`. Modifications to the source code are hot-reloaded in the notebooks thanks to `%autoreload` (useful during development).

## The system architecture

The system relies on [mitmproxy](https://mitmproxy.org/) to intercept the web traffic (both desktop and mobile), building a knowledge base with [SQLite](https://sqlite.org/) that is later accessed by a suite of web apps built with [Jupyter](https://jupyter.org/) and [Voilà](https://voila.readthedocs.io/en/stable/). [supervisor])http://supervisord.org/) is used to manage the running services. The architecture is cross platform and runs locally inside a Docker container. The system includes these running services (entry points in `/shared/services/`):

* **mitmproxy**: running the HTTP/S proxy and adding the intercepted flows to `probe.db`.
* **extractor**: reading the flows from `probe.db`, adding entities and relationships to `kb.db`.
* **nginx**: proxying all services behind http://localhost:8082.
  * **jupterlab/Voilà**: JupyterLab server with Voilà extension to serve the web apps.
  * **sqliteweb**: Web-based SQLite database browser pointing to `kb.db`.

## How to add a new extractor

 **Attention**: You are warmly invited to contribute new extractors with test data samples. Thank You!

How things are glued together:

* Extractors are in charge of scraping and extracting knowledge from the intercepted flows.
* The **mitmproxy** service operates independently. It intercepts continuously the web traffic, dumping it to `probe.db`.
* The **extractor** service is regularly pulling new flows from `probe.db`, passing them to the extractors for processing.
The pipeline is retriggered every `10` seconds and it prunes the flows older than `10` minutes, possibly reprocessing already seen flows.
This procedure ensures that recent traffic can always be inspected in `probe.db` without missing data and without retaining the complete flows history.

To add a new extractor, follow these steps:

1. Capture a sample data set of flows that contain the traffic of interest with `02 capture sample.ipynb`.  With the default configuration, you
have visibility on the flows intercepted in the last `10` minutes. You might want to use a separate browser instance without your authenticated extensions and tabs, s.t. the extracted sample data does not contain your own confidental information. Copy the `sample.db` file in the `samples` directory: you will likely need it later to run tests etc.

2. Analyze the captured flows. The notebook `03 analyze sample.ipynb` shows how to use some included utility functions to inspect and review the contents of the flows. Once you can manually extract the information you are interested in, including the data to form an UUID for the entities and the relationships, you can move forward.

3. Create a new module in `/shared/src/stratosphere/extractors` that defines a function `extract(rows: List[stratosphere.stoerage.models.Flow])`. A symbolic link to `/shared/` can be found in the top directory of JupyterLab and you can use it to add the new module. Implement the `extract` function s.t. it processes all input flows, inserting them in the knowledge base. You can use `extractor_google_search.py` as example. Recommendations:

   * You should use the class `DuplicateRows` to ensure that duplicate entities and relationships are handled correctly, merging the contents of the `data` fields. Depending on your use case, you might need to implement a custom merge strategy.
   * The fields of `Flow` ORM objects map approximately to the attributes in the `Flow` objects in mitmproxy ([official documentation](https://docs.mitmproxy.org/stable/api/mitmproxy/flow.html)). For example, the field `flow_response_content` is documented [here](https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response). The additional column `id` is a random UUID.

5. Test the new extractor extending `04 test extractors.ipynb`.

## Development

### Useful Docker parameters

Some useful options if you want to customise it:

* [--rm](https://docs.docker.com/engine/reference/run/#clean-up---rm): Docker will automatically clean up the container and remove the file system when the container exits. If you want to retain the container’s file system, remove `--rm`.
* [-p](https://docs.docker.com/engine/reference/run/#expose-incoming-ports): Publish the container's port on the host. The format is `host_ip:host_port:container_port`. If you drop the `host_ip`, the port will be published on all interfaces. By default, the proxy runs on all intefaces, but the web interface is accessible only from localhost.
* [--name](https://docs.docker.com/engine/reference/run/#name---name): Name your container. 
* [-d](https://docs.docker.com/engine/reference/run/#detached-vs-foreground): Start the container in background.
* [-it](https://docs.docker.com/engine/reference/run/#foreground): Allocate a pseudo-tty and keep STDIN open even if not attached. Useful if you want to access directly the container from terminal, via `docker execute`.
* [-v](https://docs.docker.com/engine/reference/run/#volume-shared-filesystems): Bind mount a volume.