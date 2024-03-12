# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from anvil import HtmlTemplate as _HtmlTemplate
from anvil.js import get_dom_node as _get_dom_node
from anvil.js import report_exceptions as _report_exceptions

from . import _datetime_overrides
from ._anvil_designer import TabulatorTemplate
from ._custom_modules import custom_modules
from ._defaults import (
    _default_modules,
    _default_options,
    _default_props,
    _default_table_options,
    _default_theme,
    _event_call_signatures,
    _methods,
)
from ._helpers import (
    _camelKeys,
    _ignore_resize_observer_error,
    _inject_theme,
    _merge,
    _options_property,
    _spacing_property,
    _to_module,
    _toCamel,
)
from ._js_tabulator import Tabulator as _Tabulator

row_selection_column = {
    "formatter": "rowSelection",
    "title_formatter": "rowSelection",
    "title_formatter_params": {"rowRange": "visible"},
    "width": 40,
    "hoz_align": "center",
    "header_hoz_align": "center",
    "header_sort": False,
    "cell_click": lambda e, cell: cell.getRow().toggleSelect(),
}

from ._data_loader import Query

try:
    from anvil.designer import in_designer
except ImportError:
    in_designer = False

if in_designer:
    from anvil.js.window import document

    _s = document.createElement("style")
    _s.textContent = """
.tabulator-row .tabulator-cell {
    font-style: italic;
}"""
    document.head.append(_s)


class Tabulator(TabulatorTemplate):
    theme = _default_theme
    modules = _default_modules
    default_options = _default_table_options
    _registered = False

    def __new__(cls, **properties):
        cls._setup()
        return TabulatorTemplate.__new__(cls, **properties)

    def __init__(self, **properties):
        self._t = None
        self._dom_node = dom_node = _get_dom_node(self)
        self._queued = []
        self._handlers = {}
        self._options = _merge(
            _default_options, properties, row_formatter=self._row_formatter
        )

        # public
        self.options = {}

        while dom_node.lastChild:
            dom_node.lastChild.remove()
        self.init_components(**_merge(_default_props, properties))

    @classmethod
    def _setup(cls):
        for key, val in cls.default_options.items():
            _Tabulator.defaultOptions[key] = val
        if cls._registered:
            return
        _inject_theme(cls.theme)
        cls.register_module(cls.modules)
        cls.register_module(custom_modules)
        _datetime_overrides.init_overrides()
        _ignore_resize_observer_error()
        cls._registered = True

    @staticmethod
    def register_module(modules):
        if type(modules) not in (set, tuple, list):
            modules = [modules]
        modules = [_to_module(m) for m in modules]
        _Tabulator.registerModule(modules)

    # because row_formatter is not a tabulator event but it is an anvil tabulator event
    def _row_formatter(self, row):
        self.raise_event("row_formatter", row=row)

    def _initialize(self):
        options = _camelKeys(self._options) | _camelKeys(self.options)
        options["columns"] = [_camelKeys(defn) for defn in options["columns"]]
        options["columnDefaults"] = _camelKeys(options["columnDefaults"])
        if in_designer and type(self) is Tabulator:
            pagination = options.get("pagination")
            data = [
                {
                    "columnA": "columnA",
                    "columnB": "columnB",
                    "columnC": "columnC",
                    "columnD": "columnD",
                }
            ] * 2
            if pagination:
                data *= 3
                options["paginationSize"] = 2
            options["data"] = data
            options["autoColumns"] = True

        # if we're using the rowSelection make sure things are selectable
        if (
            any(col.get("formatter") == "rowSelection" for col in options["columns"])
            and options.get("selectable") is None
            and Tabulator.default_options.get("selectable") is False
        ):
            options["selectable"] = "highlight"

        t = _Tabulator(self._dom_node, options)
        t.anvil_form = self
        self._t = t

        for meth, event, handler in self._queued:
            t[meth](event, handler)
        self._queued.clear()

    def _show(self, **event_args):
        self.remove_event_handler("show", self._show)
        self._initialize()

    def __getattr__(self, attr):
        if self._t is not None:
            attr = _toCamel(attr)
            if attr in ("setData", "replaceData"):
                self._t.clearAppTableCache()
            return getattr(self._t, attr)
        elif attr in _methods:
            msg = "Calling a method before the tabulator component is built, use the 'table_built' event"
            raise RuntimeError(msg)
        else:
            raise AttributeError(attr)

    def add_event_handler(self, event, handler):
        super().add_event_handler(event, handler)
        call_sig = _event_call_signatures.get(event)
        if call_sig is None:
            return

        def raiser(*args):
            kws = dict(zip(call_sig, args))
            return self.raise_event(event, **kws)

        self.on(event, raiser)

    def set_event_handler(self, event, handler):
        self.remove_event_handler(event)
        self.add_event_handler(event, handler)

    def remove_event_handler(self, event, handler=None):
        if handler is None:
            super().remove_event_handler(event)
        else:
            super().remove_event_handler(event, handler)
        if event in ("show", "hide") or event.startswith("x-"):
            return
        self.off(event, handler)

    @property
    def initialized(self):
        return self._t is not None and self._t.initialized

    data = _options_property("data", "getData", "setData")
    columns = _options_property("columns", None, "setColumns")
    column_defaults = _options_property("columnDefaults")
    auto_columns = _options_property("autoColumns")
    header_visible = _options_property("headerVisible")
    index = _options_property("index")
    layout = _options_property("layout")
    pagination = _options_property("pagination")
    pagination_size = _options_property("pagination_size", "getPageSize", "setPageSize")

    border = _HtmlTemplate.border
    visible = _HtmlTemplate.visible
    role = _HtmlTemplate.role
    spacing_above = _spacing_property("above")
    spacing_below = _spacing_property("below")

    def _queue_or_call(self, meth, event, handler):
        if self._t is None:
            self._queued.append([meth, _toCamel(event), handler])
        else:
            self._t[meth](_toCamel(event), handler)

    # we queue event handlers and set them on initialization
    def on(self, event, handler):
        """Add an event handler to any tablulator event (can be snake case), check the call signature from the tabulator docs"""
        with_reporting = _report_exceptions(handler)
        self._handlers[(event, handler)] = with_reporting
        self._queue_or_call("on", event, with_reporting)

    def off(self, event, handler=None):
        """Remove an event handler to any tablulator event (can be snake case)"""
        if handler is not None:
            handler = self._handlers.pop((event, handler), handler)
        self._queue_or_call("off", event, handler)

    #### for the autocomplete - removed below
    def add_row(self, row, top=True, pos=None):
        """add a row - ensure the row has an index"""

    def delete_row(self, index):
        """delete a row - the index of the row must be provided"""

    def update_row(self, index, row):
        """update a row - the index of the row must be provided"""

    def get_row(self, index):
        """get the row - the index of the row must be provided"""

    def select_row(self, index_or_indexes):
        """pass the index to select or an array of indexes"""

    def deselect_row(self, index_or_indexes=None):
        """deselect a row (single index), rows (list of indexes) or all rows (no argument)"""

    def get_selected_data(self):
        """returns a list of selected data"""

    def add_data(self, data, top=False, pos=None):
        """add data - use the keyword arguments to determine where in the table it gets added"""

    def get_data(self, active="all"):
        """
        Returns the table data based on a Tabulator range row lookup value.
        :active: Range row lookup. Valid values are: "visible", "active", "selected", "all"
        """

    def update_or_add_data(self, data):
        """checks each row and updates data if the row exists, otherwise creates a new row"""

    def replace_data(self, data=None):
        """replace all data in the table"""

    def set_filter(self, field, type=None, value=None):
        """for multiple filters pass a list of dicts with keys 'field', 'type', 'value'
        Can also pass in a function and dictionary of keyword arguments to pass to that function
        """

    def add_filter(self, field, type=None, value=None):
        """Add a filter to"""

    def remove_filter(self, field=None, type=None, value=None):
        """remove a filter"""

    def get_filters(self):
        """get a list of the current filters"""

    def clear_filter(self, clear_header=False):
        """include an arg of True to clear header filters as well"""

    def set_query(self, *args, **kws):
        """if you've used an app_table then this will set the query args and kws for the Search"""

    def clear_query(self):
        """clear the current query"""

    def clear_app_table_cache(self):
        """clear the app_table cache, you will likely want to call replace_data() after this call"""

    def set_sort(self, column, dir):
        """first argument can also be a list of sorters [{'column': field, 'dir':'asc' | 'desc'}, ...]"""

    def clear_sort(self):
        """clear the sorters"""

    def get_page(self):
        """get the current page"""

    def set_page(self, page):
        """set the current page"""


for method in _methods:
    delattr(Tabulator, method)
