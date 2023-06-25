# Cobo Safe Python SDK

A Python SDK for interactions with [Cobo Safe](https://github.com/coboglobal/cobosafe) contracts.

# Installation

```sh
pip install git+https://github.com/coboglobal/pycobosafe
```

# Usage

A sample can be found [here](./sample/sample.py).

Learn more about Cobo Safe and Cobo Argus at [Cobo Developer Hub](https://developers.cobo.com/smart-contract-custody/coboargus).

`pycobosafe` can also work as an interactive console for interacting with Cobo Safe. 

```
$> pycobosafe -c polygon-main-fork
Welcome to the cobosafe shell. Type `help` to list commands.

cobosafe > help

Documented commands (type help <topic>):
========================================
bind_authorizer    create_cobosmart  glob          safe             
bind_delegate      debug             help          sh               
chain              delegate          init_argus    unbind_authorizer
cobosafe           dump              ipython       unbind_delegate  
create_authorizer  exit              load_account
create_cobosafe    factory           py  

cobosafe > glob
Network: mainnet
Factory: 0xC0B00000e19D71fA50a9BB1fcaC2eC92fac9549C
CoboSafe: None
Safe: None
Delegate: None


cobosafe > factory
Name: CoboFactory
Address: 0x8524e4fBA45Eb8e70e22A1B9d3974DEfEe86bB42
Version: 1
Owner: 0x554e19890F4Ee596c4E43e068940dcc7C341BeCC
Latest implementations:
  CoboSafeAccount: 0x1552C84f6f09B6117dD95996d8220B37Ca6BDC4F
  FlatRoleManager: 0x07f2AD9A6299E89019793706Ae39A780b49CDdDc
  ArgusRootAuthorizer: 0xABA1D868D89F29b46499E84C73BdE47481Af8074
  CoboSmartAccount: 0xE7CA78dc87B54EF3e0Ed82cC77F449772C469414
  ArgusAccountHelper: 0x73a08503931Bd6763C4CD60013802025F1fCc3D2
  ArgusViewHelper: 0x58bF21e7a425c92C4Af55928FfA9b28a38f7d2cc


cobosafe > init_argus
CoboSafeAccount created at 0xE3dA9932f4492A28678cDe44ff875E434377bcFE
Name: CoboSafeAccount
Address: 0xE3dA9932f4492A28678cDe44ff875E434377bcFE
Version: 1
Owner: 0x765F20672A0Ff2d1fC518b7B318b72A043aaDD99
Authorizer: 0x3C85b07C8478D5876D5F17EB8dcD4D442842BaaF
Role manager: 0x324B5B185b2B02AA3A74EE44e76bc72464b020BA
Delegates: 

cobosafe > dump 0xE3dA9932f4492A28678cDe44ff875E434377bcFE
Name: CoboSafeAccount
Address: 0xE3dA9932f4492A28678cDe44ff875E434377bcFE
Version: 1
Owner: 0x765F20672A0Ff2d1fC518b7B318b72A043aaDD99
Authorizer: 0x3C85b07C8478D5876D5F17EB8dcD4D442842BaaF
Role manager: 0x324B5B185b2B02AA3A74EE44e76bc72464b020BA
Delegates: 

cobosafe > dump 0x3C85b07C8478D5876D5F17EB8dcD4D442842BaaF
Name: ArgusRootAuthorizer
Address: 0x3C85b07C8478D5876D5F17EB8dcD4D442842BaaF
Version: 1
Owner: 0x765F20672A0Ff2d1fC518b7B318b72A043aaDD99
Flags: SupportHint
Type: SetType
Tag: 
Authorizers:


cobosafe > dump 0x324B5B185b2B02AA3A74EE44e76bc72464b020BA
Name: FlatRoleManager
Address: 0x324B5B185b2B02AA3A74EE44e76bc72464b020BA
Version: 1
Owner: 0x765F20672A0Ff2d1fC518b7B318b72A043aaDD99
Delegate     Roles

cobosafe > 
```

# License

All smart contracts are released under [LGPL-3.0](./LICENSE).

# Discussion

For any concerns with the code, open an issue or visit us on Discord to discuss.

For security concerns, please email argussupport@cobo.com

