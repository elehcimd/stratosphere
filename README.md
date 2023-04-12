# **stratosphere** project

---

**stratosphere** is a free and open source OSINT platform that automatically collects and analyses every page you visit, building an internal knowledge base you can explore with a suite of customizable web apps, including:

* **Google sarch results**: Keep track of your search results
* **vk.com contacts explorer**: Explore previously seen vk.com contacts, highlighting their connections
* **Entity overview**: Navigate the knowledge base through entities and relationships

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
If you want to interrupt the execution, simply press `ctrl-C` or `cmd-c`.

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
a banner on the top left corner of the page with the text "[Tracked!]". Congratulations! **Stratosphere** is up and working.
The banner is always visible on all tracked pages.
You can now access the dashboard by clicking on it or browsing to [http://localhost:8082](http://localhost:8082).

## Core concepts

## Internals

How does it work? The system relies on [mitmproxy](https://mitmproxy.org/) to intercept your web traffic (both desktop and mobile), building a knowledge base with [SQLite](https://sqlite.org/) that is later accessed by a suite of web apps built with [Jupyter](https://jupyter.org/) and [Voilà](https://voila.readthedocs.io/en/stable/). The architecture is cross platform and runs locally inside a Docker container.



Some useful options if you want to customise it:

* [--rm](https://docs.docker.com/engine/reference/run/#clean-up---rm): Docker will automatically clean up the container and remove the file system when the container exits. If you want to retain the container’s file system, remove `--rm`.
* [-p](https://docs.docker.com/engine/reference/run/#expose-incoming-ports): Publish the container's port on the host. The format is `host_ip:host_port:container_port`. If you drop the `host_ip`, the port will be published on all interfaces. By default, the proxy runs on all intefaces, but the web interface is accessible only from localhost.
* [--name](https://docs.docker.com/engine/reference/run/#name---name): Name your container. 
* [-d](https://docs.docker.com/engine/reference/run/#detached-vs-foreground): Start the container in background.
* [-it](https://docs.docker.com/engine/reference/run/#foreground): Allocate a pseudo-tty and keep STDIN open even if not attached. Useful if you want to access directly the container from terminal, via `docker execute`.
