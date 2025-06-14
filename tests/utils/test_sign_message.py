from web3 import Web3, EthereumTesterProvider
from cheb3 import Connection

# set up the keyfile account with a known address
KEYFILE_ACCOUNT_PKEY = "0x58d23b55bc9cdce1f18c2500f40ff4ab7245df9a89505e9b1fa4851f623d241d"
KEYFILE_ACCOUNT_ADDRESS = "0xdC544d1AA88Ff8bbd2F2AeC754B1F1e99e1812fd"

# For testing purposes
class ConnectionMock(Connection):
    def __init__(self) -> None:
        self.w3 = Web3(EthereumTesterProvider())


def test_sign_raw_message_hash():
    conn = ConnectionMock()
    account = conn.account(KEYFILE_ACCOUNT_PKEY)
    msg_hash = Web3.solidity_keccak(["uint256"], [2**256 - 1])
    assert (
        account.sign_raw_message_hash(msg_hash).signature.hex()
        == "bacc1c7c0b353c261bb992549e9f8d030b46078ec31b4a8a83fbfcccd64788b1483d259536cab4408bcba2bae75f126d06483b39e7e46fa0c16c9fa6e21c527e1b"
    )
