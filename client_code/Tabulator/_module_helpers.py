# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from anvil.js.window import Function as _Function

from ._js_tabulator import Module, Tabulator

_body = """
class CustomModule extends Module {
    static moduleName = name;
    constructor(table) {
        super(table);
        cls(this, table);
    }
}
for (const key in kws) {
    CustomModule[key] = kws[key];
}

return CustomModule;
"""
_mkJsModule = _Function("Tabulator", "Module", "cls", "name", "kws", _body)
_mkJsModule = _mkJsModule.bind(None, Tabulator, Module)


def tabulator_module(name, **kws):
    def wrapper(cls):
        cls.Module = _mkJsModule(cls, name, kws)
        return cls

    return wrapper


class AbstractModule:
    #     @classmethod
    #     def __init_subclass__(cls, name, **kwargs):
    #         cls.Module = _mkJsModule(cls, name, kws)

    def __init__(self, mod, table=None):
        self.mod, self.table = mod, table
        mod.initialize = self.initialize

    def initialize(self):
        pass
