# **Extending Stratosphere**

It may be helpful to first understand Stratosphere's [architecture](/docs/architecture.md).

## How to create new Jupyter notebooks and Voilà web apps

You can access JupyterLab from the main dashboard. The notebooks located in the subdirectory `webapps` are also published as Voilà web applications.

The example notebook `01 kb overview.ipynb` shows how to query the knowledge base with SQL and Pandas. The `stratosphere` Python package is included directly from source extending the `PYTHONPATH` env variable and it is located at `/shared/src/stratosphere`. Modifications to the source code are hot-reloaded in the notebooks thanks to `%autoreload` (useful during development).

## How to add a new Extractor

 **Attention**: You are warmly invited to contribute new extractors with test data samples. Thank You!

How things are glued together:

* Extractors are in charge of scraping and extracting knowledge from the intercepted flows.
* The **mitmproxy** service operates independently. It intercepts continuously the web traffic, dumping it to `probe.db`.
* The **extractor** service regularly pulls new flows from `probe.db`, passing them to the extractors for processing.
The pipeline is retriggered every `10` seconds and it prunes the flows older than `10` minutes, possibly reprocessing already seen flows.
This procedure ensures that recent traffic can always be inspected in `probe.db` without missing data and without retaining the complete flows history.

To add a new extractor, follow these steps:

1. Capture a sample data set of flows that contain the traffic of interest with `02 capture sample.ipynb`.  With the default configuration, you
have visibility on the flows intercepted in the last `10` minutes. You might want to use a separate browser instance without your authenticated extensions and tabs, so that the extracted sample data does not contain your own confidental information. Copy the `sample.db` file in the `samples` directory: you will likely need it later to run tests etc.

2. Analyze the captured flows. The notebook `03 analyze sample.ipynb` shows how to use some included utility functions to inspect and review the contents of the flows. Once you can manually extract the information you are interested in, including the data to form an UUID for the entities and the relationships, you can move forward.

3. Create a new module in `/shared/src/stratosphere/extractors` that defines a function `extract(rows: List[stratosphere.stoerage.models.Flow])`. A symbolic link to `/shared/` can be found in the top directory of JupyterLab and you can use it to add the new module. Implement the `extract` function s.t. it processes all input flows, inserting them in the knowledge base. You can use `extractor_google_search.py` as example. Recommendations:

   * You should use the class `DuplicateRows` to ensure that duplicate entities and relationships are handled correctly, merging the contents of the `data` fields. Depending on your use case, you might need to implement a custom merge strategy.
   * The fields of `Flow` ORM objects map approximately to the attributes in the `Flow` objects in mitmproxy ([official documentation](https://docs.mitmproxy.org/stable/api/mitmproxy/flow.html)). For example, the field `flow_response_content` is documented [here](https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response). The additional column `id` is a random UUID.
   * `mitmproxy.py` is currently recording only flows whose response content type refers to tex to improve performance and reduce the database file size. If you want to capture images and other multimedia content, you might want to remove these filters.

5. Test the new extractor extending `04 test extractors.ipynb`.

## Development

My setup:

1. VSCode on the host
2. Fabric script to manage the container, see `fabfile.py`
3. Separate browser instance with enabled proxy to capture flows

### Useful Docker parameters

An overview of useful Docker parameters:

* [--rm](https://docs.docker.com/engine/reference/run/#clean-up---rm): Docker will automatically clean up the container and remove the file system when the container exits. If you want to retain the container’s file system, remove `--rm`.
* [-p](https://docs.docker.com/engine/reference/run/#expose-incoming-ports): Publish the container's port on the host. The format is `host_ip:host_port:container_port`. If you drop the `host_ip`, the port will be published on all interfaces. By default, the proxy runs on all intefaces, but the web interface is accessible only from localhost.
* [--name](https://docs.docker.com/engine/reference/run/#name---name): Name your container. 
* [-d](https://docs.docker.com/engine/reference/run/#detached-vs-foreground): Start the container in background.
* [-it](https://docs.docker.com/engine/reference/run/#foreground): Allocate a pseudo-tty and keep STDIN open even if not attached. Useful if you want to access directly the container from terminal, via `docker execute`.
* [-v](https://docs.docker.com/engine/reference/run/#volume-shared-filesystems): Bind mount a volume.
* [--cap-add=SYS_PTRACE](https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities): Allow processes to use the ptrace system call, required to run the `utils/fuser_dbs.sh` script.