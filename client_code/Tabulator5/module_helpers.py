from anvil.js.window import Function as _Function
from .js_tabulator import Tabulator, Module

_Register = _Function("Tabulator", "Module", "cls", "name", """
class CustomModule extends Module {
    constructor(table) {
        super(table);
        cls(this, table);
    }
}
CustomModule.moduleName = name;
Tabulator.registerModule(CustomModule);
""").bind(None, Tabulator, Module)


def register_module(name):
    def wrapper(cls):
        _Register(cls, name)
        return cls
    return wrapper
        

class AbstractModule:
    def __init__(self, mod, table):
        self.mod, self.table = mod, table
        mod.initialize = self.initialize

    def initialize(self):
        raise NotImplementedError
