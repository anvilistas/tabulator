from anvil import Component
from anvil.js import get_dom_node
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
        self.mod.subscribe("column-layout", self.update_definition)
    
    def update_definition(self, column):
        definition = column.definition
        self.wrap_formatters(definition)
        self.wrap_editors(definition)
    
    def wrap_formatters(self, definition):
        for suffix in "", "Print", "Clipboard", "HtmlOutput":
            option = "formatter" + suffix
            f = definition.get(option)
            if f is None or not callable(f):
                continue
            definition[option] = self.wrap(f)
        
    def wrap_editors(self, definition):
        f = definition.get("editor")
        if f is None or not callable(f):
            return
        definition["editor"] = self.wrap_editor(f)
    
    def get_call_signature(self, f):
        if not isinstance(f, type) or not issubclass(f, Component):
            return lambda cell, **params: f(cell, **params)
        elif hasattr(f, "init_components"):
            return lambda cell, **params: f(item=dict(cell.getData()), **params)
        else:
            return lambda cell, **params: f(**params)
        
    
    def setup_editor(self, component, cancel, onRendered):
        closed = {}

        def blur_cancel(e):
            # hack for datepicker
            relatedTarget = getattr(e, "relatedTarget", None)
            if not e.target.parentElement.classList.contains("anvil-datepicker") or (
                relatedTarget and relatedTarget.tagName != "SELECT"
            ):
                if closed:
                    return
                closed["x"] = True
                cancel()

        el = get_dom_node(component)
        el.addEventListener("blur", blur_cancel, True)
        el.style.padding = "8px"

        def close_editor(**event_args):
            if closed:
                return
            else:
                closed["x"] = True
            cancel()
            component.remove_from_parent()

        component.set_event_handler("x-close-editor", close_editor)

        def set_focus(*args):
            to_focus = el.querySelector(":not(div)") or el
            to_focus.focus()

        onRendered(set_focus)
        return el

    def wrap_editor(self, f):
        f = self.get_call_signature(f)
        def editor_wrapper(cell, onRendered, success, cancel, params):
            component = f(cell, **params)
            if not isinstance(component, Component):
                return
            if component.visible:
                component.visible = None
            self.table.anvilForm.add_component(component)
            return get_dom_node(component)
            
            
    @staticmethod
    def wrap(self, f):
        f = self.get_call_signature(f)
        return lambda cell, params, onRendered: f(cell, **params)