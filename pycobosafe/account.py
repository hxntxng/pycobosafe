from .factory import CoboFactory
from .gnosissafe import GnosisSafe
from .ownable import BaseOwnable
from .utils import FACTORY_ADDRESS, Operation, abi_encode_with_sig, printline


class CoboAccount(BaseOwnable):
    def __init__(self, account_addr, delegate=None) -> None:
        super().__init__(account_addr)
        self.delegate = delegate

    @property
    def authorizer(self):
        return self.contract.authorizer()

    @property
    def role_manager(self):
        return self.contract.roleManager()

    @property
    def delegates(self):
        return self.contract.getAllDelegates()

    @property
    def wallet_address(self):
        return self.contract.getAccountAddress()

    def add_delegate(self, *delegates):
        return self.contract.addDelegates(*delegates)

    def exec_transaction(
        self,
        to,
        data=b"",
        value=0,
        flag=Operation.CALL,
        use_hint=True,
        extra=b"",
        delegate=None,
    ):
        if delegate is None:
            delegate = self.delegate
        assert delegate, "delegate not set"
        tx = [flag, to, value, data, b"", extra]

        if use_hint:
            ret = self.contract.execTransaction.call(tx, {"from": delegate})

            # CallData.hint = TransactionResult.hint
            tx[4] = ret[2]
        return self.contract.execTransaction(tx, {"from": delegate})

    def exec_transaction_ex(
        self,
        to,
        func_sig,
        args,
        value=0,
        flag=Operation.CALL,
        use_hint=True,
        extra=b"",
        delegate=None,
    ):
        data = abi_encode_with_sig(func_sig, args)
        return self.exec_transaction(to, data, value, flag, use_hint, extra, delegate)

    def exec_raw_tx(
        self,
        tx,
        flag=Operation.CALL,
        use_hint=True,
        extra=b"",
        delegate=None,
    ):
        to = tx["to"]
        value = tx["value"]
        data = tx["data"]
        self.exec_transaction(to, data, value, flag, use_hint, extra, delegate)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.contract.address}>"

    def dump(self, full=False):
        super().dump(full)
        print("Authorizer:", self.authorizer)
        print("Role manager:", self.role_manager)
        print("Delegates:", ",".join(self.delegates))

        if full:
            printline()
            from .autocontract import dump

            dump(self.role_manager, full)
            printline()
            dump(self.authorizer, full)

    # Implement `transfer` interface of brownie account.
    def transfer(
        self,
        to=None,
        amount: int = 0,
        gas_limit=None,
        gas_buffer=None,
        gas_price=None,
        max_fee=None,
        priority_fee=None,
        data=None,
        nonce=None,
        required_confs: int = 1,
        allow_revert: bool = None,
        silent: bool = None,
    ):
        return self.exec_transaction(to, data, amount, delegate=self.delegate)


class CoboSafeAccount(CoboAccount):
    def __init__(self, account_addr, delegate=None, safe_owner=None) -> None:
        super().__init__(account_addr, delegate)
        self.safe_owner = safe_owner

    @property
    def safe(self):
        return GnosisSafe(self.owner, self.safe_owner)

    def enable(self):
        self.safe.enable_module(self.address)

    @classmethod
    def create(cls, safe_address, factory_address=None):
        if factory_address is None:
            factory_address = FACTORY_ADDRESS

        factory = CoboFactory(factory_address)
        account = factory.create(cls)
        account.initialize(safe_address)
        return account


class CoboSmartAccount(CoboAccount):
    def __init__(self, account_addr, delegate=None) -> None:
        super().__init__(account_addr, delegate)

    @classmethod
    def create(cls, owner_address, factory_address=None):
        if factory_address is None:
            factory_address = FACTORY_ADDRESS

        factory = CoboFactory(factory_address)
        account = factory.create(cls)
        account.initialize(owner_address)
        account.contract.addDelegate(owner_address)
        return account
