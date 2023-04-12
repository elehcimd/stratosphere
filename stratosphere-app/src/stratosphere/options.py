import copy
from contextlib import contextmanager

default_options = {
    "db": {
        "url": "sqlite:///:memory:",
        "url_probe": "sqlite:////shared/data/probe.db",
        "url_sample": "sqlite:////shared/data/sample.db",
        "url_kb": "sqlite:////shared/data/kb.db",
        "echo": False,
        "pool_pre_ping": True,
        "ask_password": False,
        "query_read_chunk_size": 1000,
        "query_write_chunk_size": 1000,
        "enable_compression": False,
    },
    "tqdm": {"disable": False, "delay": 0.2},
    "logging": {
        "stdout": True,
        "level": "INFO",
        "catch_exceptions": False,
        "clear_handlers_default_logger": True,
    },
}


class Options:
    """Handle options (preferences) for the package.

    Raises:
        RuntimeError: _description_

    Returns:
        _type_: _description_

    Yields:
        _type_: _description_
    """

    _instance = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.options = copy.deepcopy(default_options)
        return cls._instance

    def get(self, path):
        steps = path.split(".")

        d = self.options

        for step in steps:
            d = d[step]
        return d

    def set(self, path, value):
        *steps, last = path.split(".")

        d = self.options

        for step in steps:
            d = d.setdefault(step, {})
        d[last] = value

    def reset(self, path=None):
        if path is None:
            self.options = copy.deepcopy(default_options)
            return

        steps = path.split(".")
        d = default_options
        for step in steps:
            d = d[step]
        self.set(path, d)

    @contextmanager
    def option_context(self, options):
        try:
            orig_options = copy.deepcopy(self.options)
            for k, v in options.items():
                self.set(k, v)
            yield self
        finally:
            self.options = orig_options


# This object handles the options for the package, process-wide.
# To change locally the preferences, use option_context.
options = Options.instance()
