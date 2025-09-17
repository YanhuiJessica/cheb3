import pytest

from cheb3 import Connection
from cheb3.utils import compile_file, encode_with_signature

# set up the keyfile account with a known address
KEYFILE_ACCOUNT_PKEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
KEYFILE_ACCOUNT_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"


@pytest.fixture(scope="module")
def setup():
    conn = Connection("http://localhost:8545")
    return conn


@pytest.fixture(scope="module")
def account(setup):
    return setup.account(KEYFILE_ACCOUNT_PKEY)


@pytest.fixture(scope="module")
def token_contract(setup, account):
    abi, bytecode = compile_file("tests/integration/contracts/VulnWETH.sol", solc_version="0.8.20")["VulnWETH"]
    contract = setup.contract(account, abi=abi, bytecode=bytecode)
    contract.deploy()
    return contract


@pytest.fixture(scope="module")
def exploiter(setup, token_contract, account):
    abi, bytecode = compile_file("tests/integration/contracts/VulnWETHExploiter.sol", solc_version="0.8.20")[
        "VulnWETHExploiter"
    ]
    contract = setup.contract(account, abi=abi, bytecode=bytecode)
    contract.deploy(token_contract.address)
    return contract


def test_with_access_list(exploiter, token_contract):
    # avoid high SSTORE_SET_GAS in the subsequent transaction
    token_contract.functions.deposit().send_transaction(value=1)

    access_list = exploiter.functions.exploit().create_access_list(value=10)
    exploiter.functions.exploit().send_transaction(access_list=access_list, value=10)
    assert token_contract.caller.balanceOf(exploiter.address) == 2**256 - 1


def test_without_access_list(exploiter, token_contract):
    # tokens from the previous test
    assert token_contract.caller.balanceOf(exploiter.address) == 2**256 - 1
    exploiter.functions.exploit().send_transaction()
    assert token_contract.caller.balanceOf(exploiter.address) == 0


def test_with_account_access_list(exploiter, token_contract, account):
    access_list = account.create_access_list(exploiter.address, value=10, data=encode_with_signature("exploit()"))
    exploiter.functions.exploit().send_transaction(access_list=access_list, value=10)
    assert token_contract.caller.balanceOf(exploiter.address) == 2**256 - 1
