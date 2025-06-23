import pytest
from web3 import EthereumTesterProvider

from cheb3 import Connection
from cheb3.helper import Web3Helper
from cheb3.utils import compile_file, decode_data, encode_with_signature

# set up the keyfile account with a known address
KEYFILE_ACCOUNT_PKEY = "0x58d23b55bc9cdce1f18c2500f40ff4ab7245df9a89505e9b1fa4851f623d241d"
KEYFILE_ACCOUNT_ADDRESS = "0xdC544d1AA88Ff8bbd2F2AeC754B1F1e99e1812fd"

# For testing purposes
class ConnectionMock(Connection):
    def __init__(self) -> None:
        self.w3 = Web3Helper(EthereumTesterProvider())


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


def test_get_account_balance(setup, account):
    assert setup.get_balance(account.address) == 10**18
    assert account.get_balance() == 10**18


def test_connection_get_storage_at(setup, token_contract):
    assert decode_data(setup.get_storage_at(token_contract.address, 2), ["uint8"]) == 18


def test_contract_get_storage_at(token_contract):
    assert decode_data(token_contract.get_storage_at(2), ["uint8"]) == 18


def test_contract_call(token_contract):
    assert token_contract.caller.totalSupply() == 0


def test_account_call(account, token_contract):
    assert (
        account.call(token_contract.address, data=encode_with_signature("balanceOf(address)", account.address)) == b"\x00" * 32
    )
