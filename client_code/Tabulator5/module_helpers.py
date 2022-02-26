from anvil.js.window import Function as _Function
from .js_tabulator import Tabulator, Module

_Register = _Function(
    "Tabulator",
    "Module",
    "cls",
    "name",
    "kws",
    """
class CustomModule extends Module {
    constructor(table) {
        super(table);
        cls(this, table);
    }
}
CustomModule.moduleName = name;
for (const key in kws) {
    CustomModule[key] = kws[key];
}
Tabulator.registerModule(CustomModule);
""",
).bind(None, Tabulator, Module)


def register_module(name, **kws):
    def wrapper(cls):
        _Register(cls, name, kws)
        return cls

    return wrapper


class AbstractModule:
    #     @classmethod
    #     def __init_subclass__(cls, name, **kwargs):
    #         _Register(cls, name, kwargs)

    def __init__(self, mod, table):
        self.mod, self.table = mod, table
        mod.initialize = self.initialize

    def initialize(self):
        raise NotImplementedError
