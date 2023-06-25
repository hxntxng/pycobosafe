from .ownable import BaseOwnable
from .utils import s32


class FlatRoleManager(BaseOwnable):
    def get_roles(self, delegate):
        return self.contract.getRoles(delegate)

    def get_all_roles(self):
        roles = self.contract.getAllRoles()
        return [s32(i) for i in roles]

    def get_all_delegates(self):
        return self.contract.getDelegates()

    def dump(self, full=False):
        super().dump(full)
        print("Delegate", " " * 3, "Roles")
        for delegate in self.get_all_delegates():
            roles = self.get_roles(delegate)
            roles = ",".join(s32(i) for i in roles)
            print(delegate, roles)
