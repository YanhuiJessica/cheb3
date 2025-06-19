from importlib.metadata import version

from cheb3.connection import Connection

__version__ = version("cheb3")

__all__ = [
    "__version__",
    "Connection",
]
