from .account import CoboSafeAccount, CoboSmartAccount
from .ownable import ERC20, BaseOwnable
from .rolemanager import FlatRoleManager
from .utils import ETH_ADDRESS, b32, printline, s32
import yaml
import os

BASE = os.path.dirname(__file__)

def get_symbol(addr):
    if addr.lower() == ETH_ADDRESS.lower():
        return "ETH(%s)" % addr
    try:
        return "%s(%s)" % (ERC20(addr).symbol, addr)
    except Exception:
        return addr


class BaseAuthorizer(BaseOwnable):
    # flags
    HAS_PRE_CHECK_MASK = 0x1
    HAS_POST_CHECK_MASK = 0x2
    HAS_PRE_PROC_MASK = 0x4
    HAS_POST_PROC_MASK = 0x8
    SUPPORT_HINT_MASK = 0x40

    @property
    def caller(self):
        return self.contract.caller()

    @property
    def tag(self):
        try:
            return s32(self.contract.tag())
        except Exception:
            return None

    @property
    def flag(self):
        return self.contract.flag()

    @property
    def flag_str(self):
        flag = self.flag
        flags = []
        if flag & self.HAS_PRE_CHECK_MASK > 0:
            flags.append("PreCheck")
        if flag & self.HAS_POST_CHECK_MASK > 0:
            flags.append("PostCheck")
        if flag & self.HAS_PRE_PROC_MASK > 0:
            flags.append("PreProcess")
        if flag & self.HAS_POST_PROC_MASK > 0:
            flags.append("PostProcess")
        if flag & self.SUPPORT_HINT_MASK > 0:
            flags.append("SupportHint")
        return ",".join(flags)

    @property
    def type(self):
        try:
            return s32(self.contract.TYPE())
        except Exception:
            return None

    def dump(self, full=False):
        super().dump(full)
        print("Caller:", self.caller)
        print("Flags:", self.flag_str)
        print("Type:", self.type)
        print("Tag:", self.tag)

    def export_config(self, filename=None):
        if filename == None:
            filename = self.contract.name
        super().export_config(filename)
        f = open(f'{BASE}/{filename}_config.yaml','a')
        yaml.dump({"Caller":str(self.caller), "Flags":self.flag_str, "Type":self.type, "Tag":self.tag}, f)

class ArgusRootAuthorizer(BaseAuthorizer):
    @property
    def roles(self):
        role_list = []
        try:
            roles = self.contract.getAllRoles()
            role_list += [s32(i) for i in roles]
        except Exception:
            pass

        try:
            caller = self.caller
            if CoboSafeAccount.match(caller) or CoboSmartAccount.match(caller):
                role_mngr = CoboSafeAccount(caller).role_manager
                role_list += FlatRoleManager(role_mngr).get_all_roles()
        except Exception:
            pass
        return set(role_list)
    
    @property
    def delegates(self):
        delegate_to_role = {}
        try:
            caller = self.caller
            if CoboSafeAccount.match(caller) or CoboSmartAccount.match(caller):
                role_mngr = CoboSafeAccount(caller).role_manager
                delegate_list = FlatRoleManager(role_mngr).get_all_delegates()
                for delegate in delegate_list:
                    roles = FlatRoleManager(role_mngr).get_roles(delegate)
                    delegate_to_role[delegate] = ",".join(s32(i) for i in roles)
        except Exception:
            pass
        return delegate_to_role

    def get_authorizers(self, role, delegatecall=False):
        return self.contract.getAllAuthorizers(delegatecall, b32(role))

    def dump(self, full=False):
        addr = self.contract.address
        super().dump(full)

        print("Authorizers:")
        addrs = []
        for role in self.roles:
            auths = self.get_authorizers(role)
            addrs += auths
            s = []
            for auth in auths:
                name = BaseOwnable(auth).name
                s.append(f"{name}({auth})")
            print(f"  {role}", ", ".join(s))
        print("\nDelegates:")
        for delegate in self.delegates.keys():
            s = []
            print(f"   {delegate}", self.delegates[delegate])

        if full:
            for addr in addrs:
                printline()

                from .autocontract import dump

                dump(addr, full)


class TransferAuthorizer(BaseAuthorizer):
    TYPE = "TransferType"

    @property
    def tokens(self):
        return self.contract.getAllToken()

    def get_receivers(self, token):
        return self.contract.getTokenReceivers(token)

    def dump(self, full=False):
        super().dump(full)
        print("Token -> Receivers:")
        for token in self.tokens:
            receivers = self.get_receivers(token)
            token = get_symbol(token)
            print(f"  {token}", ",".join(receivers))


class FuncAuthorizer(BaseAuthorizer):
    TYPE = "FunctionType"

    @property
    def contracts(self):
        return self.contract.getAllContracts()

    def get_funcs(self, contract):
        funcs = self.contract.getFuncsByContract(contract)
        funcs = ["0x" + f.hex()[:8] for f in funcs]
        return funcs

    def dump(self, full=False):
        super().dump(full)
        print("Contract -> Functions:")
        for contract in self.contracts:
            funcs = self.get_funcs(contract)
            print(f"  {contract}", ",".join(funcs))


class BaseACL(BaseAuthorizer):
    TYPE = "CommonType"

    @property
    def contracts(self):
        return self.contract.contracts()

    def dump(self, full=False):
        super().dump(full)
        print("Contracts:", ",".join(self.contracts))

    def export_config(self, filename=None):
        if filename == None:
            filename = self.contract.name
        super().export_config(filename)
        f = open(f'{BASE}/{filename}_config.yaml','a')
        yaml.dump({"Contracts":[str(x) for x in self.contracts]}, f)

class DEXBaseACL(BaseACL):
    TYPE = "DexType"

    @property
    def in_tokens(self):
        return self.contract.getSwapInTokens()

    @property
    def out_tokens(self):
        return self.contract.getSwapOutTokens()

    @property
    def in_token_symbols(self):
        return [get_symbol(c) for c in self.in_tokens]

    @property
    def out_token_symbols(self):
        return [get_symbol(c) for c in self.out_tokens]

    def dump(self, full=False):
        super().dump(full)

        print("In tokens:", ",".join(self.in_token_symbols))
        print("Out tokens:", ",".join(self.out_token_symbols))

class FarmingBaseACL(BaseACL):
    TYPE = "CommonType"

    @property
    def whitelist_ids(self):
        return [str(x) for x in self.contract.getPoolIdWhiteList()]
    
    @property
    def whitelist_addresses(self):
        return [str(x) for x in self.contract.getPoolAddressWhiteList()]

    def dump(self, full=False):
        super().dump(full)
        print("Whitelist IDs:", ", ".join(self.whitelist_ids))
        print("Whitelist addresses:", ", ".join(self.whitelist_addresses))

    def export_config(self, filename=None):
        if filename == None:
            filename = self.contract.name
        super().export_config(filename)
        f = open(f'{BASE}/{filename}_config.yaml','a')
        yaml.dump({"Whitelist IDs":[int(x) for x in self.whitelist_ids], "Whitelist addresses":self.whitelist_addresses}, f)

class StargateWithdrawAuthorizer(FarmingBaseACL):
    def dump(self, full=False):
        super().dump(full)

    def export_config(self, filename=None):
        if filename == None:
            filename = self.contract.name
        super().export_config(filename)
        f = open(f'{BASE}/{filename}_config.yaml','a')
        