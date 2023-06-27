Making Connections
==================

To interact with the blockchain, you need to connect to a node. Since HTTP are the most common way to connect to the node in CTF, cheb3 only supports interaction with HTTP or HTTPS based JSON-RPC server and simplifies the connection process as much as possible.

.. code-block:: python

    >>> from cheb3 import Connection
    >>> conn = Connection('http://localhost:8545')

Checking the balance of an address
----------------------------------

You can use the :meth:`~cheb3.Connection.get_balance` method to check the balance of an address on the corresponding chain.

.. code-block:: python

    >>> conn.get_balance('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
    59309852122730557249293

Getting the value of a slot of a contract
-----------------------------------------

To get the raw value of a contract's storage slot, use the :meth:`~cheb3.Connection.get_storage_at` method.

.. code-block:: python

    >>> conn.get_storage_at('0x6C3e4cb2E96B01F4b866965A91ed4437839A121a', 0)
    HexBytes('0x0000000000000000000000003032ab3fa8c01d786d29dade018d7f2017918e12')

The raw value is difficult to read and use, cheb3 provides the :meth:`~cheb3.utils.decode_data` method to decode it.

.. code-block:: python

    >>> from cheb3.utils import decode_data
    >>> raw_value = conn.get_storage_at('0x6C3e4cb2E96B01F4b866965A91ed4437839A121a', 0)
    >>> decode_data(raw_value, ['address'])
    '0x3032Ab3Fa8C01d786D29dAdE018d7f2017918e12'
