from typing import Any
from hexbytes import HexBytes

from web3 import Web3
from web3.middleware import geth_poa_middleware

from cheb3.account import Account
from cheb3.contract import Contract


class Connection:
    """Creates a connection to an HTTP provider.

    :param endpoint_uri: The full URI to the RPC endpoint.
    :type endpoint_uri: str
    """

    def __init__(self, endpoint_uri: str) -> None:
        self.w3 = Web3(Web3.HTTPProvider(endpoint_uri))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise Exception(f"Could not connect to {endpoint_uri}.")

    def account(self, private_key: str = None) -> Account:
        """Creates an account associated with this connection.

        :param private_key: The private key of the account, defaults
            to :const:`None`. A new account will be created if not
            provided.
        :type private_key: str

        :rtype: :class:`Account <cheb3.account.Account>`
        """
        account_factory = Account.factory(self.w3)
        return account_factory(private_key)

    def contract(
        self,
        signer: Account = None,
        contract_name: str = "",
        address: str = None,
        **kwargs: Any,
    ) -> Contract:
        """Creates a contract instance associated with this connection.

        :param signer: The account that will sign the following transactions
            interacting with the contract, defaults to :const:`None`.
        :type signer: :class:`<cheb3.account.Account>`
        :param contract_name: The name of the contract, defaults to
            :const:`""`.
        :type contract_name: str
        :param address: Set the address of the contract if it is deployed,
            defaults to :const:`None`.

        Keyword Args:
            abi (ABI): The ABI of the contract.
            bytecode (HexStr): The bytecode of the contract.

        :rtype: :class:`Contract <cheb3.contract.Contract>`
        """
        contract_factory = Contract.factory(self.w3, contract_name)
        return contract_factory(signer, address, **kwargs)

    def get_balance(self, address: str) -> int:
        """Returns the balance of the given account.

        :param address: The address of the account.
        :type address: str

        :rtype: int
        """
        return self.w3.eth.get_balance(address)

    def get_storage_at(self, address: str, slot: int) -> HexBytes:
        """Returns the value from a storage position for the given account.

        :param address: The address of the account.
        :type address: str
        :param slot: The storage slot.
        :type slot: int

        :rtype: ~hexbytes.main.HexBytes
        """
        return self.w3.eth.get_storage_at(address, slot)
