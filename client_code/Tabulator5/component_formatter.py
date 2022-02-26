from anvil import Component
from anvil.js import get_component
from .js_tabulator import AbstractModule, register_module


@register_module("componentFormatter")
class ComponentFormatter(AbstractModule):
    def initialize(self):
        self.mod.subscribe("cell-format", self.cell_format)
        self.mod.subscribe("cell-rendered", self.cell_render)
        self.mod.subscribe("cell-delete", self.cell_delete)

    def cell_format(self, cell, component):
        if not isinstance(component, Component):
            return component
        cell.modules.format.anvilComponent = component
        if component.visible:
            component.visible = None
        self.table.anvil_form.add_component(component, slot="hidden")
        return get_dom_node(component)

    def cell_render(self, cell):
        component = cell.modules.format.get("anvilComponent")
        if component is not None and component.visible is None:
            component.visible = True

    def cell_delete(self, cell):
        component = cell.modules.format.get("anvilComponent")
        if component is not None:
            component.remove_from_parent()


@register_module("formatterWrapper", moduleInitOrder=1)
class FormatterWrapper(AbstractModule):
    def initialize(self):
        self.mod.subscribe("column-layout", self.wrap_formatters)

    def wrap_formatters(self, column):
        defintion = column.definition
        for suffix in "", "Print", "Clipboard", "HtmlOutput":
            option = "formatter" + suffix
            f = defintion.get(option)
            if f is None or not callable(f):
                continue
            defintion[option] = self.wrap(f)

    @staticmethod
    def wrap(self, f):
        if not isinstance(f, type) or not issubclass(f, Component):
            return lambda cell, params, onRendered: f(cell, **params)
        elif hasattr(f, "init_components"):
            return lambda cell, params, onRendered: f(
                item=dict(cell.getData()), **params
            )
        else:
            return lambda cell, params, onRendered: f(**params)
