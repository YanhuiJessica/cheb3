Connection
==========

Connect to a node to start interacting with the chain.

.. code-block:: python

    >>> from cheb3 import Connection
    >>> conn = Connection('http://localhost:8545')

.. note::

    After a successful connection, you can also use the native web3.py through the :attr:`w3` attribute of a Connection instance. For example,

    .. code-block:: python

        >>> conn.w3.eth.get_block_number()

.. autoclass:: cheb3.Connection
    :members: