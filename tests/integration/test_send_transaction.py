import pytest
from web3 import Web3, EthereumTesterProvider

from cheb3 import Connection
from cheb3.utils import compile_file, encode_with_signature

# set up the keyfile account with a known address
KEYFILE_ACCOUNT_PKEY = "0x58d23b55bc9cdce1f18c2500f40ff4ab7245df9a89505e9b1fa4851f623d241d"
KEYFILE_ACCOUNT_ADDRESS = "0xdC544d1AA88Ff8bbd2F2AeC754B1F1e99e1812fd"

# For testing purposes
class ConnectionMock(Connection):
    def __init__(self) -> None:
        self.w3 = Web3(EthereumTesterProvider())


@pytest.fixture(scope="module")
def setup():
    conn = ConnectionMock()
    conn.w3.eth.default_account = conn.w3.eth.accounts[0]

    conn.w3.provider.ethereum_tester.add_account(KEYFILE_ACCOUNT_PKEY)

    # fund the account
    conn.w3.eth.send_transaction(
        {
            "from": conn.w3.eth.default_account,
            "to": KEYFILE_ACCOUNT_ADDRESS,
            "value": conn.w3.to_wei(1, "ether"),
            "gas": 21000,
            "gasPrice": 10**9,
        }
    )
    return conn


@pytest.fixture(scope="module")
def account(setup):
    return setup.account(KEYFILE_ACCOUNT_PKEY)


@pytest.fixture(scope="module")
def token_contract(setup, account):
    abi, bytecode = compile_file("tests/integration/contracts/MockWETH.sol", solc_version="0.8.20")["MockWETH"]
    contract = setup.contract(account, abi=abi, bytecode=bytecode)
    contract.deploy()
    return contract


def test_contract_send_transaction(token_contract, account):
    balance_before = token_contract.caller.balanceOf(account.address)
    token_contract.functions.deposit().send_transaction(value=10)
    balance_after = token_contract.caller.balanceOf(account.address)
    assert balance_after == balance_before + 10


def test_contract_fallback(token_contract, account):
    balance_before = token_contract.caller.balanceOf(account.address)
    token_contract.fallback.send_transaction(value=10)
    balance_after = token_contract.caller.balanceOf(account.address)
    assert balance_after == balance_before + 10


def test_contract_receive(token_contract, account):
    balance_before = token_contract.caller.balanceOf(account.address)
    token_contract.receive.send_transaction(value=10)
    balance_after = token_contract.caller.balanceOf(account.address)
    assert balance_after == balance_before + 10


def test_account_fallback_with_data(account, token_contract):
    balance_before = token_contract.caller.balanceOf(account.address)
    account.send_transaction(token_contract.address, 10, b"\xde\xad\xbe\xef")
    balance_after = token_contract.caller.balanceOf(account.address)
    assert balance_after == balance_before + 10 + 0xDEADBEEF


def test_account_send_transaction(account, token_contract):
    balance_before = token_contract.caller.balanceOf(account.address)
    account.send_transaction(token_contract.address, 10, encode_with_signature("deposit()"))
    balance_after = token_contract.caller.balanceOf(account.address)
    assert balance_after == balance_before + 10
