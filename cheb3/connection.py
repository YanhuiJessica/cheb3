import subprocess
from typing import Any
from hexbytes import HexBytes
from requests.exceptions import ConnectionError

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from cheb3.account import Account
from cheb3.contract import Contract


class Connection:
    """Creates a connection to an HTTP provider.

    :param endpoint_uri: The full URI to the RPC endpoint.
    :type endpoint_uri: str
    """

    def __init__(self, endpoint_uri: str) -> None:
        self.w3 = Web3(Web3.HTTPProvider(endpoint_uri))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        try:
            self.w3.is_connected(show_traceback=True)
        except Exception as e:
            if isinstance(e, ConnectionError):
                raise Exception(f"Could not connect to {endpoint_uri}.")
            # HTTPError('400 Client Error: Bad Request for url'): connected but is_connected() returns False

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

    def cast_call(self, to: str, signature: str, *_args, **kwargs) -> str:
        """Use cast with default settings to interact with a smart contract
        without creating a new transaction on the blockchain.
        View `Foundry book <https://book.getfoundry.sh/reference/cast/cast-call>`_ for more details.

        :param to: The address of the target contract.
        :type to: str
        :param signature: The function signature.
        :type signature: str
        :param `*args`: Function arguments.

        Keyword Args:
            from (str): Specifies the address of the sender.
        """
        args = []
        for a in _args:
            if isinstance(a, (int, list)):
                args.append(str(a))
            elif isinstance(a, bool):
                args.append(str(a).lower())
            else:
                args.append(a)
        options = ["--rpc-url", self.w3.provider.endpoint_uri]
        if "from" in kwargs:
            options.extend(["--from", kwargs["from"]])
        ret = subprocess.run(
            [
                "cast",
                "call",
                *options,
                to,
                signature,
                *args,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if ret.returncode != 0:
            err = ret.stderr.decode().strip()
            raise Exception(err[err.find("Context:"):])
        ret = ret.stdout.decode().strip()
        return ret

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

    def get_code(self, address: str) -> HexBytes:
        """Returns the code at the given account.

        :param address: The address of the account.
        :type address: str

        :rtype: ~hexbytes.main.HexBytes
        """
        return self.w3.eth.get_code(address)
