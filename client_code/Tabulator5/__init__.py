# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from anvil import HtmlTemplate as _HtmlTemplate
from anvil.js import get_dom_node as _get_dom_node

from . import _datetime_overrides
from ._anvil_designer import Tabulator5Template
from ._custom_modules import custom_modules
from ._helpers import _camelKeys, _ignore_resize_observer_error, _merge, _toCamel
from ._js_tabulator import Tabulator as _Tabulator
from ._js_tabulator import TabulatorModule as _TabulatorModule

_event_call_signatures = {
    "row_click": ("event", "row"),
    "cell_click": ("event", "cell"),
    "row_tap": ("event", "row"),
    "cell_tap": ("event", "cell"),
    "cell_edited": ("cell",),
    "page_loaded": ("pageno",),
    "row_selected": ("row",),
    "row_deselected": ("row",),
    "row_selectetion_change": ("data", "rows"),
}

_default_options = {
    "auto_columns": False,
    "header_visible": True,
    "height": "",
    "index": "id",
    "layout": "fitColumns",
    "pagination": True,
    "pagination_size": 10,
    "data": None,
    "columns": [],
    "column_defaults": {},
}

_default_props = {
    "spacing_above": "small",
    "spacing_below": "small",
    "border": "",
    "visible": True,
}

row_selection_column = {
    "formatter": "rowSelection",
    "titleFormatter": "rowSelection",
    "width": 40,
    "hozAlign": "center",
    "headerHozAlign": "center",
    "headerSort": False,
    "cellClick": lambda e, cell: cell.getRow().toggleSelect(),
}

_warnings = {}


def _options_property(key, getMethod=None, setMethod=None):
    def option_getter(self):
        if getMethod is None or self._t is None:
            return self._options.get(key)
        else:
            return self._t[getMethod]()

    def option_setter(self, value):
        self._options[key] = value
        if self._t is None:
            return
        elif setMethod is not None:
            return self._t[setMethod](value)
        elif _warnings.get("post_init") is not None:
            return
        _warnings["post_init"] = True
        print(
            f"Warning: chaning the option {key!r} after the table has been built has no effect"
        )

    return property(option_getter, option_setter)


_default_modules = {
    "Edit",
    "Filter",
    "Format",
    "FrozenColumns",
    "FrozenRows",
    "Interaction",
    "Menu",
    "Page",
    "ResizeColumns",
    "ResizeTable",
    "SelectRow",
    "Sort",
}

_default_options = {"layout": "fitColumns", "selectable": False}


class Tabulator5(Tabulator5Template):
    modules = _default_modules
    default_options = _default_options
    _registered = False

    @classmethod
    def _setup(cls):
        if cls._registered:
            return
        cls.register_module(cls.modules)
        cls.register_module(custom_modules)
        _datetime_overrides.init_overrides()
        for key, val in cls.default_options.items():
            _Tabulator.defaultOptions[key] = val
        cls._registered = True
        _ignore_resize_observer_error()

    @staticmethod
    def register_module(modules):
        if type(modules) not in (set, tuple, list):
            modules = [modules]

        def name_to_module(modname):
            if not isinstance(modname, str):
                return modname
            if not modname.endswith("Module"):
                modname += "Module"
            return _TabulatorModule[modname]

        modules = [name_to_module(mod) for mod in modules]
        _Tabulator.registerModule(modules)

    def __new__(cls, **properties):
        cls._setup()
        return Tabulator5Template.__new__(cls, **properties)

    def __init__(self, **properties):
        self._t = None
        self._el = el = _get_dom_node(self)
        self._queued = []
        self._handlers = {}
        self._options = _merge(
            _default_options, properties, row_formatter=self._row_formatter
        )

        # public
        self.options = {}

        el.replaceChildren()
        self.init_components(**_merge(_default_props, properties))

    def _row_formatter(self, row):
        # because row_formatter is not a tabulator event but it is an anvil tabulator event
        self.raise_event("row_formatter", row=row)

    def _initialize(self):
        options = _camelKeys(self._options)
        options["columns"] = [_camelKeys(defn) for defn in options["columns"]]
        options["columnDefaults"] = _camelKeys(options["columnDefaults"])
        options.update(_camelKeys(self.options))
        data = options.pop("data")

        t = _Tabulator(self._el, options)
        t.anvil_form = self
        for attr, args, kws in self._queued:
            getattr(t, attr)(*args, **kws)
        self._queued.clear()
        # use setData - initiating data with anything other than list[dict] breaks tabulator

        def built():
            t.setData(data)
            self._t = t

        t.on("tableBuilt", built)

    def _show(self, **event_args):
        if self._t is None:
            self._initialize()

    def __getattr__(self, attr):
        attr = _toCamel(attr)
        if self._t is None:
            return lambda *args, **kws: self._queued.append([attr, args, kws])
        return getattr(self._t, attr)

    def add_event_handler(self, event, handler):
        super().add_event_handler(event, handler)
        call_sig = _event_call_signatures.get(event)
        if call_sig is None:
            return

        def raiser(*args):
            kws = dict(zip(call_sig, args))
            return self.raise_event(event, **kws)

        self._handlers[(event, handler)] = raiser
        self.on(_toCamel(event), raiser)

    set_event_handler = add_event_handler

    def remove_event_handler(self, event, handler):
        super().remove_event_handler(event, handler)
        self.off(_toCamel(event), self._handlers.pop((event, handler), None))

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

    #### for the autocomplete
    def on(self, tabulator_event, handler):
        """Add an event handler to any tablulator event"""

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

    def replace_data(self, data):
        """replace all data in the table"""

    def set_filter(self, field, type=None, value=None):
        """for multiple filters pass a list of dicts with keys 'field', 'type', 'value'
        Can also pass in a function and dictionary of keyword arguments to pass to that function"""

    def add_filter(self, field, type=None, value=None):
        """Add a filter to"""

    def remove_filter(self, field=None, type=None, value=None):
        """remove a filter"""

    def get_filters(self):
        """get a list of the current filters"""

    def clear_filter(self, clear_header=False):
        """include an arg of True to clear header filters as well"""

    def set_sort(self, column, dir):
        """first argument can also be a list of sorters [{'column': field, 'dir':'asc' | 'desc'}, ...]"""

    def clear_sort(self):
        """clear the sorters"""


methods = (
    "on",
    "add_row",
    "delete_row",
    "update_row",
    "get_row",
    "select_row",
    "deselect_row",
    "get_selected_data",
    "add_data",
    "get_data",
    "update_or_add_data",
    "replace_data",
    "set_filter",
    "add_filter",
    "remove_filter",
    "get_filters",
    "clear_filter",
    "set_sort",
    "clear_sort",
)

for method in methods:
    delattr(Tabulator5, method)
