from anvil import Component
from anvil.js import get_dom_node
from .module_helpers import AbstractModule, register_module

@register_module("componentFormatter")
class ComponentFormatter(AbstractModule):
    def initialize(self):
        self.mod.subscribe("cell-format", self.cell_format)
        self.mod.subscribe("cell-rendered", self.cell_render)
        self.mod.subscribe("cell-delete", self.cell_delete)

    def cell_format(self, cell, component):
        if not isinstance(component, Component):
            return component
        cell.modules.anvilComponent = component
        if component.visible:
            component.visible = None
        self.table.anvil_form.add_component(component)
        return get_dom_node(component)

    def cell_render(self, cell):
        component = cell.modules.get("anvilComponent")
        if component is not None and component.visible is None:
            component.visible = True

    def cell_delete(self, cell):
        component = cell.modules.get("anvilComponent")
        if component is not None:
            component.remove_from_parent()


def cell_wrapper(f):
    if not isinstance(f, type) or not issubclass(f, Component):
        return lambda cell, **params: f(cell, **params)
    elif hasattr(f, "init_components"):
        return lambda cell, **params: f(item=dict(cell.getData()), **params)
    else:
        return lambda cell, **params: f(**params)


class AbstractCallableWrapper(AbstractModule):
    options = []
    def initialize(self):
        self.mod.subscribe("column-layout", self.update_definition)

    def update_definition(self, column):
        definition = column.definition
        for option in self.options:
            f = definition.get(option)
            if f is None or not callable(f):
                continue
            definition[option] = self.wrap(f)
    
    @staticmethod
    def wrap(f):
        raise NotImplemented

@register_module("formatterWrapper", moduleInitOrder=1)
class FormatterWrapper(AbstractCallableWrapper):
    options = ["formatter" + suffix for suffix in ("", "Print", "Clipboard", "HtmlOutput")]

    @staticmethod
    def wrap(f):
        f = cell_wrapper(f)
        return lambda cell, params, onRendered: f(cell, **params)


@register_module("sorterWrapper", moduleInitOrder=1)
class SorterWrapper(AbstractCallableWrapper):
    options = ["sorter"]

    @staticmethod
    def wrap(f):
        def sorter_wrapper(a, b, aRow, bRow, column, dir, params):
            return f(a, b, **params)
        return sorter_wrapper

def setup_editor(component, cell, onRendered, success, cancel):
    check = {"closed": False}
    sentinel = object()

    def close_editor(value=sentinel, **event_args):
        if check["closed"]:
            return
        else:
            check["closed"] = True
        if value is not sentinel:
            success(value)
        else:
            cancel()
        component.remove_from_parent()

    def blur_cancel(e):
        # hack for datepicker
        rt = getattr(e, "relatedTarget", None)
        if rt is None or rt.closest(".daterangepicker") is None:
            close_editor()

    def set_focus(*args):
        if component.visible is None:
            component.visible = True
        to_focus = el.querySelector(":not(div)") or el
        to_focus.focus()

    component.set_event_handler("x-close-editor", close_editor)
    if component.visible:
        component.visible = None

    el = get_dom_node(component)
    el.style.padding = "4px"
    el.addEventListener("blur", blur_cancel, True)

    onRendered(set_focus)
    return el


@register_module("editorWrapper", moduleInitOrder=1)
class EditorWrapper(AbstractCallableWrapper):
    options = ["editor"]

    def initialize(self):
        super().initialize()
        self.mod.subscribe("edit-cancelled", self.edit_cancelled)

    def edit_cancelled(self, cell):
        component = cell.modules.get("anvilEditComponent")
        if component is None:
            return
        if component.parent is not None:
            cell.getElement().blur()
            component.remove_from_parent()
        cell.modules.anvilEditComponent = None

    @staticmethod
    def wrap(f):
        f = cell_wrapper(f)
        def editor_wrapper(cell, onRendered, success, cancel, params):
            component = f(cell, **params)
            if not isinstance(component, Component):
                return
            cell.getTable().anvil_form.add_component(component)
            cell._cell.modules.anvilEditComponent = component
            return setup_editor(component, cell, onRendered, success, cancel)
        return editor_wrapper
