import pkg_resources

from cheb3.connection import Connection

__version__ = pkg_resources.get_distribution("cheb3").version

__all__ = [
    "__version__",
    "Connection",
]
