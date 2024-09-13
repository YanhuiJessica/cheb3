Interaction Basis
=================

An account is required to sign transactions. In cheb3, accounts are associated with connections.

To get an account instance, you can either use the existing private key or create a new one.

.. code-block:: python

    >>> new_account = conn.account()
    >>> existing_account = conn.account("<private-key>")

Working with Contracts
----------------------

Compiling Source Code
~~~~~~~~~~~~~~~~~~~~~

To get the ABI and bytecode of a contract, you can use :meth:`~cheb3.utils.compile_sol` or :meth:`~cheb3.utils.compile_file` to compile from a source string or a file.

.. code-block:: python

    >>> from cheb3.utils import compile_sol
    >>> abi, bytecode = compile_sol('''
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;

    import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

    contract Cheb3Token is ERC20 {
        constructor(string memory _name, string memory _symbol) ERC20(_name, _symbol) {
            _mint(msg.sender, 100);
        }
    }
    ''',
    solc_version="0.8.17",  # choose compiler version
    base_path="node_modules/" # to include source code from other directories
    )["Cheb3Token"] # choose the expected contract

If you are working on a Hardhat/Foundry project, you can use :meth:`~cheb3.utils.load_compiled` to reuse the project compilation results.

.. code-block:: python

    >>> from cheb3.utils import load_compiled
    >>> abi, bytecode = load_compiled(
        "Token.sol",    # the contract file
        "Cheb3Token"    # the contract name, default to the filename without suffix
    )

Interacting with Existing Contracts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

cheb3 provides two ways to interact with existing contracts.

Using ABI
*********

If you have the contract's ABI, you can create a contract instance:

.. code-block:: python

    >>> contract = conn.contract(
        account,    # specified the signer
        address=contract_addr,
        abi=abi
    )

After that, the interaction with the contract is similar to that in `web3.py <https://web3py.readthedocs.io/en/stable/examples.html#interacting-with-existing-contracts>`_. Since the contract instance is associated with an account, cheb3 simplifies the process of signing and sending transactions. Take the previously compiled Cheb3Token for example:

.. code-block:: python

    >>> to_addr = "0xAcF2f2575dFe641B350fE671f2Eb7E796A4ba402"
    >>> contract.functions.balanceOf(account.address).call()    # call a view function
    100
    >>> tx_receipt = contract.functions.transfer(to_addr, 10).send_transaction()
    1970-01-01 xx:xx:xx.xxx | INFO     | cheb3.contract:send_transaction:236 - (0x4427aF9505D7E800bC2401239023fDA97415999d).transfer transaction hash: 0xcb47f4f1f57db6080cc0abb6bcf4aaae5940bea858b06ef4a0f18984a1f983c6
    >>> contract.caller.balanceOf(to_addr)  # another way to call a view function
    10

Using Function Signatures
*************************

If you feel lazy to provide the ABI, you can interact with the contract using function signatures:

.. code-block:: python

    >>> from cheb3.utils import encode_with_signature
    >>> tx_receipt = account.send_transaction(
        contract_addr,
        data=encode_with_signature("transfer(address,uint256)", to_addr, 10)
    )
    1970-01-01 xx:xx:xx.xxx | INFO     | cheb3.account:send_transaction:99 - Transaction to 0x4427aF9505D7E800bC2401239023fDA97415999d: 0x7b363957f43044f3b599ba7bc8e6e07fa5e5c80c149baddebd24a136c570f86c
    >>> 
    >>> from cheb3.utils import decode_data
    >>> decode_data(
        account.call(
            contract_addr,
            data=encode_with_signature("balanceOf(address)", account.address)
        ),
        ["uint256"]
    )
    80

More easily, if you have `Foundry <https://book.getfoundry.sh/>`_ installed, you can interact with contracts using ``cast`` (currently only supports simple ``cast call``):

.. code-block:: python

    >>> conn.cast_call(
        contract_addr,
        "balanceOf(address)(uint)",
        account.address
    )
    '5000000000000000 [5e15]'

Deploying New Contracts
~~~~~~~~~~~~~~~~~~~~~~~

With the ABI and bytecode, you can create a contract instance and deploy it:

.. code-block:: python

    >>> contract = conn.contract(account, abi=abi, bytecode=bytecode)
    >>> contract.deploy("Cheb3Token", "CT") # with constructor arguments
    1970-01-01 xx:xx:xx.xxx | DEBUG    | cheb3.contract:deploy:94 - Deploying contract ...
    1970-01-01 xx:xx:xx.xxx | INFO     | cheb3.contract:deploy:99 - The contract is deployed at 0x4427aF9505D7E800bC2401239023fDA97415999d

After the deployment, you can continue to use this instance without creating a new one.

If the proxy parameter is set to :const:`True`, a minimal proxy contract will be deployed and connected to the logic contract:

.. code-block:: python

    >>> contract.deploy("Cheb3TokenWithProxy", "CTWP", proxy=True)
    1970-01-01 xx:xx:xx.xxx | DEBUG    | cheb3.contract:deploy:94 - Deploying contract ...
    1970-01-01 xx:xx:xx.xxx | INFO     | cheb3.contract:deploy:99 - The logic contract is deployed at 0x86CEf5e7Fb9171478135AB27A1885049465F6fA5
    1970-01-01 xx:xx:xx.xxx | DEBUG    | cheb3.contract:deploy:116 - Deploying the proxy ...
    1970-01-01 xx:xx:xx.xxx | INFO     | cheb3.contract:deploy:121 - The proxy is deployed at 0x8F1d8d499709f4BA4DC28F60068398335435B07C

Another way to deploy a contract with only bytecode is to use :meth:`~cheb3.account.Account.send_transaction`:

.. code-block:: python

    >>> example_bytecode = "0x600a600c600039600a6000f3602a60005260206000f3"
    >>> contract_addr = account.send_transaction(
        None,   # to zero address
        data=example_bytecode
    ).contractAddress
    1970-01-01 xx:xx:xx.xxx | INFO     | cheb3.account:send_transaction:99 - Transaction to None: 0x30b022a47d60dc17be88d5d5da7e4ca0985cbe2abb722cd24bb1a6a4d6931f39