import cmd
import os

from web3 import Web3

from .account import CoboSafeAccount, CoboSmartAccount
from .factory import CoboFactory
from .gnosissafe import GnosisSafe
from .utils import (
    FACTORY_ADDRESS,
    b32,
    connect_new_chain,
    get_address_url,
    get_all_support_chains,
    get_current_chain,
    load_account,
    rand_salt,
)


class CoboSafeConsole(cmd.Cmd):
    """
    An interactive command console to use cobosafe tools.
    """

    prompt = "cobosafe > "

    def __init__(self) -> None:
        super().__init__()

        self.debug = False
        self.factory_address = FACTORY_ADDRESS
        self.delegate_address = None

        self.reset()

    def reset(self):
        # Changes along the network.
        self.safe_address = None
        self.cobosafe_address = None

    ##################################################################
    # Console related functions.

    def _arg_as_addr(self, arg, default_value=None):
        if arg:
            assert Web3.isAddress(arg), f"{arg} is not valid address"
            return Web3.toChecksumAddress(arg)
        return default_value

    def onecmd(self, line):
        try:
            # ! run system shell.
            # ? eval python script.
            if line.startswith("!"):
                line = "sh " + line[1:]
            elif line.startswith("?"):
                line = "py " + line[1:]

            return super().onecmd(line)
        except Exception as e:
            print("Error: ", e)
            if self.debug:
                raise Exception from e

            cmd = line.split()[0]
            super().onecmd(f"help {cmd}")
            return False  # don't stop

    def start_console(self):
        """
        Start a cobosafe console. Catch Ctrl+C.
        """
        print("Welcome to the cobosafe shell. Type `help` to list commands.\n")
        while True:
            try:
                self.cmdloop()
                return
            except KeyboardInterrupt:
                print()  # new line.

    def single_command(self, cmd, debug=True):
        """
        Run single command. This will not catch call exception by default.
        """
        if type(cmd) is list:
            cmd = " ".join(cmd)
        else:
            cmd = str(cmd)

        self.debug = debug
        self.onecmd(cmd)

    # Console commands

    def do_debug(self, arg):
        """
        debug: Toggle debug flag. Once on, the console will raise exceptions instead of catching them.
        """
        self.debug = not self.debug
        print("debug set to", self.debug)

    def do_exit(self, arg):
        """
        exit: Exit the shell.
        """

        print("bye!")
        return True

    def do_ipython(self, arg=None):
        """
        ipython: Start ipython console.
        """
        console = self  # noqa
        if self.safe_address:
            safe = GnosisSafe(self.safe_address)  # noqa
        if self.cobosafe_address:
            cobosafe = CoboSafeAccount(  # noqa
                self.cobosafe_address, self.delegate_address
            )
        factory = CoboFactory()  # noqa
        __import__("IPython").embed(colors="Linux")

    def do_sh(self, arg):
        """
        sh <cmd>: Run system shell command.
        """
        os.system(arg)

    def do_py(self, arg):
        """
        py <expr>: Eval python script.
        """
        print(eval(arg.strip()))

    def do_url(self, arg):
        """
        url <address>: Open XXXScan URL.
        """
        url = get_address_url(arg)
        print(url)
        self.do_sh(f"open {url}")

    # Network and account.

    def do_chain(self, arg):
        """
        chain : Print current chain config.
        chain <chain> : Change chain.
        """
        ALIAS = {
            "eth": "mainnet",
            "arb": "arbitrum-main",
            "op": "optimism-main",
            "bsc": "bsc-main",
            "matic": "polygon-main",
            "avax": "avax-main",
        }
        new_chain = ALIAS.get(arg, arg)

        chains = get_all_support_chains()
        cur_chain = get_current_chain()
        if new_chain not in chains:
            print("Current network:", cur_chain)
            print("Supported networks: ", ",".join(chains))
            return

        if new_chain and new_chain != cur_chain:
            connect_new_chain(new_chain)
            print(f"Change to {new_chain}")

            # Clear this if we change chain.
            self.reset()

        self.do_glob(arg)

    def do_glob(self, arg):
        """
        glob: Print current global config.
        """
        print("Network:", get_current_chain())
        print("Factory:", self.factory_address)
        print("CoboSafe:", self.cobosafe_address)
        print("Safe:", self.safe_address)
        print("Delegate:", self.delegate_address)

    def do_load_account(self, arg):
        """
        load_account <private key>: Load from raw private key.
        load_account <wallet name>: Load from key store file.
        https://eth-brownie.readthedocs.io/en/stable/account-management.html
        """
        addr = str(load_account(arg))
        print("Load address:", addr)
        self.do_delegate(addr)

    # Cobo safe setting commands

    def do_safe(self, arg):
        """
        safe : Print current Safe address.
        safe <address> : Set Safe address.
        """
        addr = self._arg_as_addr(arg)
        if addr:
            self.safe_address = addr
            print(f"Safe set to {self.safe_address}")

            # auto set cobosafe.
            try:
                cobosafe = CoboFactory().get_cobosafe(addr)
                if cobosafe:
                    self.do_cobosafe(cobosafe)
            except Exception:
                pass
        else:
            print(f"Current Safe: {self.safe_address}")

    def do_cobosafe(self, arg):
        """
        cobosafe : Print current CoboSafe address.
        cobosafe <address> : Set CoboSafe address.
        """
        addr = self._arg_as_addr(arg)
        if addr:
            self.cobosafe_address = addr
            print(f"CoboSafe set to {self.cobosafe_address}")
        else:
            print(f"Current CoboSafe: {self.cobosafe_address}")

    def do_delegate(self, arg):
        """
        delegate : Print current delegate address.
        delegate <address> : Set delegate address.
        """
        addr = self._arg_as_addr(arg)
        if addr:
            self.delegate_address = addr
            print(f"Delegate set to {self.delegate_address}")
        else:
            print(f"Current delegate: {self.delegate_address}")

    # Cobo safe view commands

    def do_factory(self, arg):
        """
        factory [<address>]: Print CoboFactory information.
        """
        factory_address = self._arg_as_addr(arg)
        if factory_address and factory_address != self.factory_address:
            print(f"Factory changes from {self.factory_address} to {factory_address}")
            self.factory_address = factory_address
        else:
            factory_address = self.factory_address

        factory = CoboFactory(factory_address)
        factory.dump()

    def do_dump(self, arg):
        """
        dump <address> [<verbose>]: Print contract information by name.
        """
        args = arg.split()
        addr = self._arg_as_addr(args[0])

        from .autocontract import dump

        dump(addr, len(args) > 1)
    
    def do_export_config(self, arg):
        args = arg.split()
        addr = self._arg_as_addr(args[0])

        from .autocontract import export_config

        export_config(addr)

    # Cobo safe interaction commands

    def do_create_cobosafe(self, arg):
        """
        create_cobosafe <safe>: Create CoboSafeAccount
        """
        safe = self._arg_as_addr(arg, self.safe_address)
        assert safe, "safe not set"
        a = CoboSafeAccount.create(safe)
        print("Created:")
        a.dump()

    def do_create_cobosmart(self, arg):
        """
        create_cobosmart <owner>: Create CoboSmartAccount
        """
        owner = self._arg_as_addr(arg, self.delegate_address)
        assert owner, "owner not set"
        a = CoboSmartAccount.create(owner)
        print("Created:")
        a.dump()

    def _call_helper(self, func, args):
        assert self.safe_address, "safe not set"
        safe = GnosisSafe(self.safe_address)
        factory = CoboFactory()
        helper_addr = factory.get_address("ArgusAccountHelper")
        safe.delegate_call(helper_addr, func, args)

    def do_init_argus(self, arg):
        """
        init_argus:
            init argus for safe
            (Call ArgusAccountHelper.initArgus)
        """
        factory = CoboFactory()
        self._call_helper("initArgus(address,bytes32)", [factory.address, rand_salt()])
        cobosafe = factory.get_cobosafe(self.safe_address)
        print(f"CoboSafeAccount created at {cobosafe}")
        self.do_dump(cobosafe)
        self.do_cobosafe(cobosafe)

    def do_bind_delegate(self, arg):
        """
        bind_delegate <role> <delegate address> :
            Bind role and delegate to CoboSafe.
            (Call ArgusAccountHelper.grantRoles)
        """
        assert self.cobosafe_address, "cobosafe not set"
        role, delegate = arg.split()
        delegate = self._arg_as_addr(delegate)
        role = b32(role)
        self._call_helper(
            "grantRoles(address,bytes32[],address[])",
            [self.cobosafe_address, [role], [delegate]],
        )

    def do_unbind_delegate(self, arg):
        """
        unbind_delegate <role> <delegate address> :
            Unbind role and delegate to CoboSafe.
            (Call ArgusAccountHelper.revokeRoles)
        """
        assert self.cobosafe_address, "cobosafe not set"
        role, delegate = arg.split()
        delegate = self._arg_as_addr(delegate)
        role = b32(role)
        self._call_helper(
            "revokeRoles(address,bytes32[],address[])",
            [self.cobosafe_address, [role], [delegate]],
        )

    def do_create_authorizer(self, arg):
        """
        create_authorizer <name> :
            Create authorizer for CoboSafe
            (Call ArgusAccountHelper.createAuthorizer)
        """
        assert arg, "name not set"
        name = b32(arg)
        factory = CoboFactory()
        tag = rand_salt()
        auth_addr = factory.contract.getCreate2Address(self.safe_address, name, tag)
        self._call_helper(
            "createAuthorizer(address,address,bytes32,bytes32)",
            [self.factory_address, self.cobosafe_address, name, tag],
        )
        print(f"Created at {auth_addr}")
        self.do_dump(auth_addr)

    def do_bind_authorizer(self, arg):
        """
        bind_authorizer <role> <authorizer address> :
            Add authorizer to root authorzer of CoboSafe
            (Call ArgusAccountHelper.addAuthorizer)
        """
        role, auth = arg.split()
        auth = self._arg_as_addr(auth)
        role = b32(role)
        self._call_helper(
            "addAuthorizer(address,address,bool,bytes32[])",
            [self.cobosafe_address, auth, True, [role]],
        )

    def do_unbind_authorizer(self, arg):
        """
        unbind_authorizer <role> <authorizer address> :
            Remove authorizer from root authorzer of CoboSafe
            (Call ArgusAccountHelper.removeAuthorizer)
        """
        role, auth = arg.split()
        auth = self._arg_as_addr(auth)
        role = b32(role)
        self._call_helper(
            "removeAuthorizer(address,address,bool,bytes32[])",
            [self.cobosafe_address, auth, True, [role]],
        )
