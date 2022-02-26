from anvil import Component
from anvil.js import get_component
from .js_tabulator import AbstractModule, register_module

@register_module("componentFormatter")
class ComponentFormatter(AbstractModule):
    def initialize(self):
        self.mod.subscribe("cell-format", self.cell_format)
        self.mod.subscribe("", self.cell_init)

    def cell_format(self, cell, prev):
        if isinstance(prev, Component):
            return get_dom_node(prev)
        return prev


