Contract
========

To create a contract instance with the given contract address, using the ABI from Foundry compiled output:

.. code-block:: python

    >>> from cheb3.utils import load_compiled
    >>> abi, bytecode = load_compiled("Token.sol", "Cheb3Token")
    >>> contract = conn.contract(
        account,    # specified the signer
        contract_addr,
        abi=abi
    )

Or, you can create an undeployed contract instance and then deploy it.
Its address will be stored in its :attr:`address` attribute:

.. code-block:: python

    >>> contract = conn.contract(
        account,    # specified the signer
        abi=abi,
        bytecode=bytecode
    )
    >>> contract.deploy("Cheb3Token", "CT")

.. autoclass:: cheb3.contract.Contract
    :special-members: __init__
    :members:

Calling the contract functions
------------------------------

Cheb3 wraps :class:`~web3.contract.ContractFunction`, enabling the use of all web3.py contract function interaction methods. And it provides two additional methods: :meth:`~cheb3.contract.ContractFunctionWrapper.send_transaction` and :meth:`~cheb3.contract.ContractFunctionWrapper.create_access_list`.

:meth:`~cheb3.contract.ContractFunctionWrapper.send_transaction` allows signing and sending the transaction directly with the account associated with the contract instance.

.. code-block:: python

    >>> contract.functions.myMethod(*args).send_transaction()

:meth:`~cheb3.contract.ContractFunctionWrapper.create_access_list` can create an EIP-2930 type access list based on the function call data.

.. code-block:: python

    >>> access_list = contract.functions.myMethod(*args).create_access_list()
    >>> contract.functions.myMethod(*args).send_transaction(access_list=access_list)

.. autoclass:: cheb3.contract.ContractFunctionWrapper
    :members: