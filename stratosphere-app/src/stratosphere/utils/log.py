import inspect
import logging
import sys
import time
from typing import Callable, Dict, Optional

from colorama import Back, Fore, Style

from stratosphere.options import options
from stratosphere.utils.environment import is_notebook, is_tty

logger = logging.getLogger("stratosphere")


class ColoredFormatter(logging.Formatter):
    """
    Handles the formatting of coloured logging messages.
    """

    def __init__(self, *args, colors: Optional[Dict[str, str]] = None, **kwargs) -> None:
        """Create a new color formatter.

        Args:
            colors (Optional[Dict[str, str]], optional): . Dictionary of colors and logging levels. Defaults to None.
            args: args to pass to logging.Formatter.
            kwargs: kwargs to pass to logging.Formatter.
        """
        super().__init__(*args, **kwargs)
        self.colors = colors if colors else {}

    def format(self, record) -> str:  # noqa
        """Format the record as coloured text

        Args:
            record (_type_): logging record to format.

        Returns:
            str: Resulting formatted coloured logging message.
        """

        record.color = self.colors.get(record.levelname, "")
        record.reset = Style.RESET_ALL
        return super().format(record)


def init_logging():
    """Logging intialization."""

    if options.get("logging.clear_handlers_default_logger"):
        # Drop other default handlers, otherwise we might end up with
        # duplicate log entries to stdout.
        logging.getLogger().handlers.clear()

    # Get logger and clear the handlers.
    logger = logging.getLogger("stratosphere")
    logger.handlers.clear()
    logger.setLevel(getattr(logging, options.get("logging.level")))

    if options.get("logging.stdout"):
        if is_tty() or is_notebook():
            formatter = ColoredFormatter(
                "{color}■{reset} {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
                colors={
                    "DEBUG": Fore.CYAN,
                    "INFO": Fore.GREEN,
                    "WARNING": Fore.YELLOW,
                    "ERROR": Fore.RED,
                    "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
                },
            )

        else:
            formatter = logging.Formatter("[%(levelname)s] %(message)s")

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def timeit(f: Callable) -> Callable:
    """Decorator to measure the call execution time.

    Args:
        f (Callable): Function to execute

    Returns:
        Callable: Function with decorator.
    """

    def timed(*args, **kw):
        ts = time.perf_counter()
        result = f(*args, **kw)
        te = time.perf_counter()
        logger.info(f"Elapsed time @{f.__name__}: {(te - ts):.2f}s")
        return result

    return timed


class IgnoredChainedCallLogger:
    """
    This class is designed to catch chained operations, logging that they won't
    be executed, and returning nicely."""

    def __getitem__(self, index):
        """Catching all field requests, logging them.

        Args:
            index (_type_): index to be resolved.

        Returns:
            IgnoredChainedCallLogger: Recursive instance of the same class.
        """
        logger.error(f"Ignoring chained operation: .[{index}]")
        return IgnoredChainedCallLogger()

    def __getattribute__(self, name):
        """Catching all attribute requests, logging them.

        Args:
            name (_type_): name to be resolved.

        Returns:
            IgnoredChainedCallLogger: Recursive instance of the same class.
        """

        if name == "_ipython_canary_method_should_not_exist_":
            # this is handled separately, to handle how ipython is
            # managing the objects at the end of cells.
            raise AttributeError()

        if name in ["_repr_html_", "__str__"]:
            # empty output.

            return lambda: ""

        if name not in ["__class__", "_ipython_display_"]:
            # in case a new chained operation is requested, log it.
            logger.error(f"Ignoring chained operation: .{name}(...)")

        def newfunc(*args, **kwargs):
            # recursive instantiation of IgnoredChainedCallLogger
            return IgnoredChainedCallLogger()

        return newfunc

    @staticmethod
    def _repr_html_() -> str:
        """HTML representation, empty: we already produce the logging output.

        Returns:
            str: Empty string.
        """
        return ""


def fatal(*args, **kwargs):
    """Handle fatal situations, logging them and handling over the execution
    to IgnoredChainedCallLogger to log chained operations.

    Returns:
        IgnoredChainedCallLogger: Logger of chained opeartions.
    """

    logger.error(*args, **kwargs)
    return IgnoredChainedCallLogger()


def default_exception_handler(func: Callable) -> Callable:
    """Decorator Handle exceptions occurring in chained function calls.
    e.g., (a().b().c())
    It does not always work with subscripts, e.g., x[123].

    Args:
        func (Callable): Function to decorate.

    Returns:
        Callable: Decorated function.
    """

    def inner_function(*args, **kwargs):
        if not options.get("logging.catch_exceptions"):
            return func(*args, **kwargs)
        else:
            try:
                return func(*args, **kwargs)
            except (KeyboardInterrupt, TypeError, Exception) as e:
                if type(e) == KeyboardInterrupt:
                    return fatal("Keyboard interrupt.")
                else:
                    return fatal(f"{compact_exception_message(e)}.")

    return inner_function


def compact_exception_message(e):
    """Construct string representing , in a compact way, the traceback, useful to handle exceptions.

    Args:
        e (_type_): Raised exception.

    Returns:
        _type_: _description_
    """

    exc_type, exc_value, exc_traceback = sys.exc_info()
    frame = inspect.trace()[-1]

    details = {
        "file": exc_traceback.tb_frame.f_code.co_filename,
        "lineno": exc_traceback.tb_lineno,
        "type": exc_type.__name__,
        "message": str(exc_value),
        "trace": f'{frame.filename}:{frame.lineno}::{frame.function} "{frame.code_context[frame.index].strip()}"',
    }

    return f'{details["type"]} at {details["trace"]}: {details["message"]}'
