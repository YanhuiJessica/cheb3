import pytest
from web3 import EthereumTesterProvider

from cheb3 import Connection
from cheb3.helper import Web3Helper
from cheb3.utils import compile_file, encode_with_signature, calc_create_address

# For testing purposes
class ConnectionMock(Connection):
    def __init__(self) -> None:
        self.w3 = Web3Helper(EthereumTesterProvider())


@pytest.fixture(scope="module")
def setup():
    conn = ConnectionMock()
    return conn


@pytest.fixture(scope="module")
def account1(setup):
    pkey = setup.w3.provider.ethereum_tester.backend.account_keys[0]
    return setup.account(pkey)


@pytest.fixture(scope="module")
def account2(setup):
    pkey = setup.w3.provider.ethereum_tester.backend.account_keys[1]
    return setup.account(pkey)


@pytest.fixture(scope="module")
def delegate_contract(setup, account1):
    abi, bytecode = compile_file("tests/integration/contracts/SimpleDelegateContract.sol", solc_version="0.8.20")[
        "SimpleDelegateContract"
    ]
    contract = setup.contract(account1, abi=abi, bytecode=bytecode)
    contract.deploy()
    return contract


@pytest.fixture(scope="module")
def token_contract(setup, account1):
    abi, bytecode = compile_file("tests/integration/contracts/MockWETH.sol", solc_version="0.8.20")["MockWETH"]
    contract = setup.contract(account1, abi=abi, bytecode=bytecode)
    contract.deploy()
    return contract


def test_set_code_deployment(setup, account1):
    abi, bytecode = compile_file("tests/integration/contracts/MockWETH.sol", solc_version="0.8.20")["MockWETH"]
    contract = setup.contract(account1, abi=abi, bytecode=bytecode)
    contract_addr = calc_create_address(account1.address, setup.w3.eth.get_transaction_count(account1.address))
    signed_auth = account1.sign_authorization(contract_addr)
    contract.deploy(authorization_list=[signed_auth])
    # authorization_list is removed
    assert setup.get_code(account1.address).to_0x_hex() == f"0x"


def test_self_set_code(setup, account1, account2, token_contract, delegate_contract):
    signed_auth = account1.sign_authorization(delegate_contract.address)
    token_contract.functions.deposit().send_transaction(value=10, authorization_list=[signed_auth])

    assert setup.get_code(account1.address).to_0x_hex() == f"0xef0100{delegate_contract.address[2:].lower()}"

    account1_balance_before = token_contract.caller.balanceOf(account1.address)
    account2_balance_before = token_contract.caller.balanceOf(account2.address)
    account2.send_transaction(
        account1.address,
        data=encode_with_signature(
            "execute((bytes,address,uint)[])",
            [
                (
                    bytes.fromhex(encode_with_signature("transfer(address,uint)", account2.address, 5)[2:]),
                    token_contract.address,
                    0,
                )
            ],
        ),
    )
    account1_balance_after = token_contract.caller.balanceOf(account1.address)
    account2_balance_after = token_contract.caller.balanceOf(account2.address)
    assert account1_balance_after == account1_balance_before - 5
    assert account2_balance_after == account2_balance_before + 5

    reset_auth = account1.sign_authorization(f"0x{'00' * 20}")
    token_contract.functions.deposit().send_transaction(value=10, authorization_list=[reset_auth])

    assert setup.get_code(account1.address).hex() == f""


def test_other_set_code(setup, account1, account2, token_contract, delegate_contract):
    signed_auth = account1.sign_authorization(delegate_contract.address, is_sender=False)
    account2.send_transaction(
        token_contract.address,
        10,
        encode_with_signature("deposit()"),
        authorization_list=[signed_auth],
    )

    assert setup.get_code(account1.address).to_0x_hex() == f"0xef0100{delegate_contract.address[2:].lower()}"
