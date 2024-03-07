from .authorizer import BaseAuthorizer
from .ownable import BaseOwnable


def convert(addr):
    def _sub_classes(cls):
        for sub_cls in cls.__subclasses__():
            yield sub_cls
            yield from _sub_classes(sub_cls)

    sub_cls = set(_sub_classes(BaseOwnable))

    base = BaseOwnable(addr)
    name = base.name

    if name is None:
        # Not valid IVersion contract.
        return None

    for cls in sub_cls:
        if cls.__name__ == name:
            return cls(addr)

    base_auth = BaseAuthorizer(addr)
    typ = base_auth.type

    if typ is None:
        return base

    for cls in sub_cls:
        if getattr(cls, "TYPE", None) == typ:
            return cls(addr)

    return base_auth


def dump(addr, full=False):
    obj = convert(addr)
    if obj:
        obj.dump(full)
    else:
        print("No valid IVersion contract.")

def export_config(addr):
    obj = convert(addr)
    if obj:
        obj.export_config(obj.name)
    else:
        print("No valid IVersion contract.")