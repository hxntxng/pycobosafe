import random

from brownie import accounts

from .ownable import BaseOwnable
from .utils import FACTORY_ADDRESS, ZERO_ADDRESS, b32, s32


class CoboFactory(BaseOwnable):
    def __init__(self, address=FACTORY_ADDRESS) -> None:
        super().__init__(address)

    def get_address(self, name):
        addr = self.contract.getLatestImplementation(b32(name))
        if addr == ZERO_ADDRESS:
            return None
        return addr

    def get_all_names(self):
        names = self.contract.getAllNames()
        names = [s32(i) for i in names]
        return names

    def get_cobosafe(self, safe):
        addr = self.contract.getLastRecord(safe, b32("CoboSafeAccount"))
        if addr == ZERO_ADDRESS:
            return None
        return addr

    def get_all_impls(self):
        r = {}
        for name in self.get_all_names():
            r[name] = self.get_address(name)
        return r

    def create(self, name_or_cls, deployer=None):
        if type(name_or_cls) is str:
            name = b32(name_or_cls)
            create_wrapper = False
        else:
            name = b32(name_or_cls.__name__)
            create_wrapper = True

        if deployer is None:
            deployer = accounts.default

        proxy = self.contract.create.call(name, {"from": deployer})
        self.contract.create(name, {"from": deployer})

        if create_wrapper:
            return name_or_cls(proxy)
        else:
            return proxy

    def create2(self, name_or_cls, salt=None, deployer=None):
        if type(name_or_cls) is str:
            name = b32(name_or_cls)
            create_wrapper = False
        else:
            name = b32(name_or_cls.__name__)
            create_wrapper = True

        if salt is None:
            salt = random.randbytes(32)

        if deployer is None:
            deployer = accounts.default

        proxy = self.contract.getCreate2Address(deployer, name, salt)
        self.contract.create2(name, salt, {"from": deployer})

        if create_wrapper:
            return name_or_cls(proxy)
        else:
            return proxy

    def dump(self, full=False):
        super().dump(full)
        names = self.get_all_names()
        print(f"Latest implementations (Total {len(names)}):")
        for name in names:
            addr = self.get_address(name)
            print(f"  {name}: {addr}")
