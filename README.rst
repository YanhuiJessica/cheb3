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

Examples of using `cheb3` in CTF challenges can be found in `/examples <examples/>`_.

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