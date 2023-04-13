# **stratosphere** project

---

**stratosphere** is a free and open source OSINT platform that automatically collects every page you visit, building a private knowledge base you can analyze with Jupyter notebooks and explore with an extensible suite of simple web apps:

* **Google sarch results**: Review your past Google search results
* **vk.com contacts explorer**: Explore previously seen vk.com contacts, highlighting their connections
* **Entity overview**: Navigat

You can use the platform also to reverse-engineer HTTP/HTTPS web requests, including REST APIs. This lets you unlock the potential of private REST APIs, investigate GDPR breaches, and **implement new scrapers to extend the knowledge base**.

---

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

#### Check

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
a banner `[Tracked!]` on the top left corner of the page. Congratulations! **Stratosphere** is up and working.
The banner is always visible on all tracked pages.
You can now access the dashboard by clicking on it or browsing to [http://localhost:8082](http://localhost:8082).

## Core concepts

### The knowledge base

* The knowledge base is stored as an SQlite database (`/shared/data/kb.db`) with two tables: `entities` and `relationships`. An entity describes a "thing", such as a web search result or an user. A relationship describes the connenction between entities, such as a friendship between users.
* Entities are uniquely identified by UUIDs that are generated by hashing their unique string identifiers. The definition of the unique string identifier is not fixed and it depends on the scraper that extracted it. For example, the entity of an user with ID `"123"` on social network `"xyz.com"` could be uniquely identified by the string `"xyz.com-123"`. Its UUID is defined by the 32-character hexadecimal string obtained from `UUID(hex=MD5("xyz.com-123"))`. The MD5 hashing algorithm, despite being cryptographically insecure, remains a sound choice in this context thanks to the length of its hashes (128 bits), that can be used with no further transformation as UUIDs. Each entity contains these attributes:

  - `id`:
  - `type`:
  - `data`:
  - `blob`:
  - `ts`:

* Relationships are uniquely identified by the UUIDs obtained from hashing the concatenation of their UUIDs. For example, the relationship between entities with UUIDs `"A.."` and `"B.."` is defined as `UUID(hex=MD5("A..B.."))`. Each entity contains these attributes:

  - `id`:
  - `type`:
  - `src`:
  - `dst`:
  - `data`:
  - `blob`:
  - `ts`:

### Adding new Jupyter notebooks and Voilà web apps

You can access Jupyter lab from the main dashboard. The notebooks located in the subdirectory `webapps` are also published as Voilà web applications.
The example notebook `01 kb overview.ipynb` shows how to query the knowledge base with SQL and Pandas.

### Adding a new scraper


* Flows (raw web requests and responses) are dumped in the `flows` table in the SQLite database `probe.db`. The flows are regularly processed by the scrapers before being removed, ensuring that the file size remains under control. The columns in this table map to the attributes in the `Flow` objects in mitmproxy ([official documentation](https://docs.mitmproxy.org/stable/api/mitmproxy/flow.html)). For example, the contents and meaning of field `flow_response_content` is documented [here](https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response).


* `02 capture sample.ipynb` lets you capture a sample of flows for later analysis.
* `03 analyze sample.ipynb` helps you analyze the contents of a captured sample of flows.
* `04 test extractors.ipynb` tests the extractors on the captured flow samples.


## Development

### How does it work?

The system relies on [mitmproxy](https://mitmproxy.org/) to intercept the web traffic (both desktop and mobile), building a knowledge base with [SQLite](https://sqlite.org/) that is later accessed by a suite of web apps built with [Jupyter](https://jupyter.org/) and [Voilà](https://voila.readthedocs.io/en/stable/). The architecture is cross platform and runs locally inside a Docker container.

### Useful Docker parameters

Some useful options if you want to customise it:

* [--rm](https://docs.docker.com/engine/reference/run/#clean-up---rm): Docker will automatically clean up the container and remove the file system when the container exits. If you want to retain the container’s file system, remove `--rm`.
* [-p](https://docs.docker.com/engine/reference/run/#expose-incoming-ports): Publish the container's port on the host. The format is `host_ip:host_port:container_port`. If you drop the `host_ip`, the port will be published on all interfaces. By default, the proxy runs on all intefaces, but the web interface is accessible only from localhost.
* [--name](https://docs.docker.com/engine/reference/run/#name---name): Name your container. 
* [-d](https://docs.docker.com/engine/reference/run/#detached-vs-foreground): Start the container in background.
* [-it](https://docs.docker.com/engine/reference/run/#foreground): Allocate a pseudo-tty and keep STDIN open even if not attached. Useful if you want to access directly the container from terminal, via `docker execute`.
* [-v](https://docs.docker.com/engine/reference/run/#volume-shared-filesystems): Bind mount a volume. For development and persistance, you can mount the absolute path of the `stratosphere-app` directory to `/shared` with `-v /absolute-path-to-stratosphere-repos/stratosphere-app/:/shared`. On Windows, the host path (before `:`) must be a valid Windows path.