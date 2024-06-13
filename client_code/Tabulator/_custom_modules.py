# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork
from functools import partial

from anvil import Component
from anvil.js import get_dom_node, report_exceptions
from anvil.js.window import Function, document, window

from ._helpers import assert_no_suspension
from ._module_helpers import AbstractModule, tabulator_module

JsProxy = type(document)


@tabulator_module("cssClassAdder")
class CssClassAdder(AbstractModule):
    def __init__(self, mod, table):
        super().__init__(mod, table)
        mod.registerTableOption("cssClass", None)

    def initialize(self):
        classes = self.table.options.get("cssClass")
        if classes is None:
            return
        elif isinstance(classes, str):
            classes = [classes]

        self.table.element.classList.add(*classes)


@tabulator_module("componentFormatter")
class ComponentFormatter(AbstractModule):
    def initialize(self):
        self.mod.subscribe("cell-format", self.cell_format)
        self.mod.subscribe("cell-rendered", self.cell_render)
        self.mod.subscribe("cell-delete", self.cell_delete)
        # because we don't support onRendered callbacks
        self.mod.registerColumnOption("cellRender", None)
        self.mod.registerColumnOption("cellRenderParams", None)

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
        renderCallback = cell.column.definition.get("cellRender", None)
        if renderCallback:
            renderParams = cell.column.definition.get("cellRenderParams", None) or {}
            if callable(renderParams):
                renderParams = renderParams()
            renderCallback(cell.getComponent(), **renderParams)

    def cell_delete(self, cell):
        component = cell.modules.get("anvilComponent")
        if component is not None:
            component.remove_from_parent()


def cell_wrapper(f):
    if not isinstance(f, type) or not issubclass(f, Component):
        return lambda cell, **params: f(cell=cell, **params)
    elif hasattr(f, "init_components"):
        # TODO - this could break if trying to use as both an editor and a headerFilter
        def render_form(cell, **params):
            data = cell.getData("data")
            if type(data) is JsProxy:
                data = dict(data)
            return f(item=data, cell=cell, **params)

        return render_form
    else:
        return lambda cell, **params: f(**params)


class AbstractCallableWrapper(AbstractModule):
    options = []

    def initialize(self):
        self.mod.subscribe("column-layout", self.update_definition, 10)

    def update_definition(self, column):
        definition = column.definition
        for option in self.options:
            f = definition.get(option)
            if f is None or not callable(f):
                continue
            definition[option] = report_exceptions(assert_no_suspension(self.wrap(f)))

    @staticmethod
    def wrap(f):
        return f


@tabulator_module("formatterWrapper", moduleInitOrder=-10)
class FormatterWrapper(AbstractCallableWrapper):
    options = [
        "formatter" + suffix for suffix in ("", "Print", "Clipboard", "HtmlOutput")
    ]

    @staticmethod
    def wrap(f):
        f = cell_wrapper(f)
        return lambda cell, params, onRendered: f(cell, **params)


@tabulator_module("sorterWrapper", moduleInitOrder=-10)
class SorterWrapper(AbstractCallableWrapper):
    options = ["sorter"]

    @staticmethod
    def wrap(f):
        def sorter_wrapper(a, b, aRow, bRow, column, dir, params):
            return f(a, b, **params)

        return sorter_wrapper


@tabulator_module("headerFilterFuncWrapper", moduleInitOrder=-10)
class HeaderFilterFuncWrapper(AbstractCallableWrapper):
    options = ["headerFilterFunc"]

    @staticmethod
    def wrap(f):
        def header_filter_func(header_val, row_val, row_data, params):
            return f(header_val, row_val, row_data, **params)

        return header_filter_func


@tabulator_module("paramLookup", moduleInitOrder=-10)
class ParamLookupWrapper(AbstractCallableWrapper):
    options = [
        "headerFilterParams",
        "titleFormatterParams",
        "sorterParams",
        "formatterParams",
        "editorParams",
        "headerFilterFuncParams",
    ]


def setup_editor(component, cell, onRendered, success, cancel):
    # if cell is None then we're being used as a HeaderFilterComponent
    # the blur events and remove_from_parent are no longer relevant
    check = {"closed": False}
    sentinel = object()

    def close_editor(value=sentinel, **event_args):
        if check["closed"] and cell is not None:
            return
        else:
            check["closed"] = True
        if value is not sentinel:
            success(value)
        else:
            cancel()
        if cell is not None:
            component.remove_from_parent()

    def blur_cancel(e):
        if cell is None:
            return
        # hack for datepicker
        rt = getattr(e, "relatedTarget", None)
        if rt is None or rt.closest(".daterangepicker") is None:
            close_editor()

    el = document.createElement("div")
    el.style.height = "100%"
    el.style.display = "flex"
    el.style.alignItems = "center"
    el.style.padding = "8px"
    el.append(get_dom_node(component))
    to_focus = el.querySelector(":not(div)") or el

    def set_focus(*args):
        if component.visible is None:
            component.visible = True
        to_focus.focus()

    component.set_event_handler("x-close-editor", close_editor)

    def x_success(value, **event_args):
        return close_editor(value=value, **event_args)

    component.set_event_handler("x-success", x_success)
    component.set_event_handler("x-cancel", partial(close_editor, value=sentinel))

    if component.visible and cell is not None:
        component.visible = None

    to_focus.addEventListener("blur", blur_cancel)

    onRendered(set_focus)
    return el


@tabulator_module("editorWrapper", moduleInitOrder=-10)
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
            if hasattr(cell, "_cell"):
                cell.getTable().anvil_form.add_component(component)
                cell._cell.modules.anvilEditComponent = component
            else:
                # then it might be a cellWrapper because we're a headerFilter edit component
                cell.getColumn().getTable().anvil_form.add_component(component)
                cell = None
            return setup_editor(component, cell, onRendered, success, cancel)

        return editor_wrapper


@tabulator_module("headerFilterWrapper", moduleInitOrder=-10)
class HeaderFilterWrapper(AbstractCallableWrapper):
    options = ["headerFilter"]

    @staticmethod
    def wrap(f):
        def header_filter_wrapper(cellWrapper, onRendered, success, cancel, params):
            component = f(**params)
            if not isinstance(component, Component):
                return
            cellWrapper.getColumn().getTable().anvil_form.add_component(component)
            return setup_editor(component, None, onRendered, success, cancel)

        return header_filter_wrapper


@tabulator_module("scrollPosMaintainer")
class ScrollPosMaintainer(AbstractModule):
    # fix annoying scroll to top after page changes when no height is set
    def initialize(self):
        if not self.table.options.pagination:
            return
        self.mod.subscribe("page-changed", self.page_changed)
        self.mod.subscribe("data-refreshed", self.page_loaded)
        self.x = self.y = 0
        self.page_changing = False

    def page_changed(self):
        if self.page_changing:
            return
        if self.table.options.height:
            return
        self.page_changing = True
        self.x, self.y = window.scrollX, window.scrollY

    def page_loaded(self):
        if not self.page_changing:
            return
        self.page_changing = False
        window.scrollTo(self.x, self.y)


generate_wrapper = Function(
    "generate",
    "update_mod",
    "type",
    """
function generateWrapper(defaultOptions, userOptions = {}) {
    const allowed = new Set([...Object.keys(this.registeredDefaults), ...Object.keys(defaultOptions)]);
    const userKeys = new Set(Object.keys(userOptions));
    const RE_SNAKE = new RegExp("_[a-z]", "g");
    const toCamel = (s) => s.replace(RE_SNAKE, (m) => m[1].toUpperCase());

    for (const key of userKeys) {
        if (allowed.has(toCamel(key))) {
            userKeys.delete(key);
        }
    }
    if (userKeys.size) {
        update_mod(type, userKeys);
    }
    return generate.call(this, defaultOptions, userOptions);
}
return generateWrapper;
""",
)


@tabulator_module("optionVerifier")
class OptionVerifier(AbstractModule):
    # don't ignore bad options
    def __init__(self, mod, table):
        super().__init__(mod, table)
        generate = table.optionsList.generate
        table.optionsList.generate = generate_wrapper(
            generate, self.check_keys, "table"
        )
        generate = table.columnManager.optionsList.generate
        table.columnManager.optionsList.generate = generate_wrapper(
            generate, self.check_keys, "column"
        )

    @report_exceptions
    def check_keys(self, type, bad_keys):
        if not bad_keys:
            return
        msg = f"The following {type} option(s) are invalid: {', '.join(map(repr, bad_keys))}.\n"
        msg += "You may need to include the required Module in Tabulator.modules."
        raise AttributeError(msg)


from ._data_loader import CustomDataLoader, QueryModule

custom_modules = [
    cls.Module
    for cls in (
        CssClassAdder,
        ComponentFormatter,
        EditorWrapper,
        FormatterWrapper,
        SorterWrapper,
        HeaderFilterFuncWrapper,
        HeaderFilterWrapper,
        CustomDataLoader,
        QueryModule,
        ParamLookupWrapper,
        ScrollPosMaintainer,
        OptionVerifier,
    )
]
