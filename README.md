# **stratosphere** Project

## Team Members

* Michele Dallachiesa, michele.dallachiesa@sigforge.com
* Eric Brichetto, brichett13@gmail.com
* Perry Borst, perryborst@gmail.com
* Duplorers

## Tool Description
**stratosphere** is a free and open source OSINT platform that automatically collects every page you visit, building a private knowledge base you can analyze with Jupyter notebooks and an extensible suite of web apps including:

* **LinkedIn contacts and companies explorer**: Explore previously browsed LinkedIn profiles and companies
* **Google search results**: Review your past Google search results
* **vk.com contacts explorer**: Explore previously seen vk.com contacts, highlighting their connections
* **Flows overview**: Overview of web traffic intercepted in the last 10 minutes

You can also use the platform to quickly reverse-engineer HTTP/HTTPS web requests, including REST APIs. This lets you unlock the potential of private REST APIs, investigate GDPR breaches, and implement new scrapers to extend the knowledge base and power new web apps.

## Installation

**stratosphere** runs in a Docker container and uses [mitmproxy](https://mitmproxy.org/) to intercept web traffic for analysis.
The following steps will install the image and set up your browser to use the proxy. 

### 1. Install Docker

Docker is a tool that is used to automate the deployment of applications in lightweight containers so that
applications can work efficiently in different environments.
You can follow the [official installation instructions](https://docs.docker.com/get-docker/).

### 2. Pull the image and start the container

Before running the image, set Docker Preferences > Resources > Memory to 4GB. In Windows, this is set using the [.wslconfig file](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#configure-global-options-with-wslconfig).

You can now download and run the image from the command line:

```
docker pull micheda/stratosphere-app:latest

docker run --rm --name stratosphere-app -p 8080:8080 -p 127.0.0.1:8082:8082 \
  micheda/stratosphere-app:latest
```

After executing the last command, the container is running in foreground, 
with all services reporting a `successful` status.
To stop the container, simply press `ctrl-c` or `cmd-c`.

> To build the image yourself, `docker build -t stratosphere-app .` from the `stratosphere-app` directory of this repository will do the trick.

### 3. Configure your browser or device

You need to configure your browser or device to route all traffic through the HTTP proxy listening on `http://localhost:8080`.

Browser versions and configurations frequently change, you should search the web on how to configure an HTTP proxy for your system.
Some operating systems have a global settings, some browsers have their own, other applications use environment variables, etc. I recommend FoxyProxy, a browser extension that let you quickly switch between different proxy settings:

* [Firefox](https://addons.mozilla.org/it/firefox/addon/foxyproxy-standard/)
* [Chrome, Brave](https://chrome.google.com/webstore/detail/foxyproxy-standard/gcknhkkoolaabfmlnjonogaaifnjlfnp?hl=it)

### 4. Install the mitmproxy Certificate Authority

With the container running, and your browser set to direct traffic to `http://localhost:8080`, check that your web traffic is going through the container's mitmproxy by browsing to http://mitm.it.
It should present you with a simple page to install the mitmproxy Certificate Authority. 
Follow the instructions for your OS / system and install the CA.

### 5. Test the web tracking

From this point, **stratosphere** should be tracking all web pages you visit, and gathering data.
You can test that the system is working properly by browsing to https://www.google.com and verifying the presence of
a banner displaying `[Tracked]` or `[S]` on the top left corner of the page. 

![Example of tracked banner](/docs/images/tracked-banner-example.jpg)

The banner is always visible on all tracked pages. If missing, try refreshing the page with `ctrl-r`. Congratulations! **Stratosphere** is up and working properly.

### 6. Viewing dashboard data

The Dashboard allows you to analyze the pages you have visited. 
You can access the dashboard by browsing to [http://localhost:8082](http://localhost:8082). 

![Stratosphere Dashboard and options](/docs/images/dashboard.jpg)

Dashboard Options include:
* Flow Analysis : Google Search Results
* Web apps directory: Extractors that scrape pages (??), e.g. vk.com, LinkedIn
* Object analysis: SQLite web interface (??) and Jupyter Lab notebooks (??)


***Note:*** You may see the message `WARNING: No mounted volume detected on /shared`, informing you
that the newly captured information, analyses, and any other modification is lost once the Docker container is terminated.
If you want to persist the data, follow the next optional step.

### 7. Persisting your changes (optional)

You can persist your changes (including the knowledge base, analyses, custom extractors and analyses) by 
mounting the `stratosphere-app` directory of this repository on the `/shared` mount point in the container.

Firstly, clone this repository and verify the absolute path of the directory you want to mount:

```
git clone https://github.com/elehcimd/stratosphere.git
cd stratosphere/stratosphere-app
pwd
```

Assuming that the absolute path to the directory is `/xyz/stratosphere-app`, 
execute the following from the command line. On Windows, the host path (before `":"`) must be an absolute Windows directory path (e.g. `C://OSINT_Utils/stratosphere-app`).

```
docker run -d --rm --name stratosphere-app -p 8080:8080 -p 127.0.0.1:8082:8082 \
  -v /xyz/stratosphere-app:/shared micheda/stratosphere-app:latest
```

The additional parameter `-v` takes care of mounting the volume, `-d` runs the container in background.
You can stop the container with the following command:

```
docker stop stratosphere-app
```

## Usage 

### LinkedIn contacts explorer

**stratosphere**  automatically fetches people and company profiles as you explore and browse on linkedin.com, adding them to the database for later analysis.

In the following example, the user explored a few contacts and their connections on linkedin.com.
![LinkedIn profile page](/docs/images/linkedin-explorer-01.png)

Links from those results are displayed in the Google Search Notebook:
![Overview of profiles and relationships (companies) on linkedin.com](/docs/images/linkedin-explorer-03.png)


### Flow Analysis
### Webapps
#### Google Search

**stratosphere**  automatically fetches links from Google searches and adds them to the database for further query. 

In the following example, the user has searched for 'Tenzing Norgay' on Google.
![Results from Tenzing Norgay search on Google](/docs/images/tenzing-googlesearch.jpg)

Links from those results are displayed in the Google Search Notebook:
![Results from Tenzing Norgay search in Google Search Notebook](/docs/images/tenzing-googlesearch-notebook.jpg)

### Extending Functionality
You can add new Jupyter notebooks to analyze data from existing extractors, or new extractors to parse specific sites. 
See [Extending Stratosphere](/docs/extend.md).

## Additional Information
* Potential Next steps
* Limitations
* Architecture Decisions
The project uses UUIDs to identify entities (e.g. user, search result) and relationships between entities. 
If an entity is encountered several times, potentially on different web pages, a stable UUID lets us 
consolidate the knowledge in a unifying entity, merging the different data points.
The process of generating UUIDs for entities was thus designed to be solid and robust.
Further details on architecture can be found in [System Architecture](/docs/architecture.md). 