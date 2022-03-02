from ._anvil_designer import Tabulator5Template
from anvil.js import get_dom_node as _get_dom_node
from .utils import _toCamel, _merge_from_default, _ignore_resize_observer_error, _camelKeys
from .js_tabulator import Tabulator as _Tabulator, TabulatorModule as _TabulatorModule
from anvil import HtmlTemplate as _HtmlTemplate

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

def _options_property(key, getMethod=None, setMethod=None):
    def option_getter(self):
        if getMethod is None or self._t is None:
            return self._options.get(key)
        else:
            return self._t[getMethod]()
    
    def option_setter(self, value):
        self._options[key] = value
        if setMethod is not None and self._t is not None:
            return self._t[setMethod](value)
    
    return property(option_getter, option_setter)

_modules = ("Format", "Page", "Interaction", "Sort", "Edit", "Filter", "Menu", "SelectRow", "FrozenColumns", "FrozenRows", "ResizeColumns")

class _DummyTabulator:
    def __init__(self):
        self.queued = []
    
    def __getattr__(self)

class Tabulator5(Tabulator5Template):
    modules = _modules
    default_options = {"layout": "fitColumns", "selectable": False}
    _registered = False

    @classmethod
    def _setup(cls):
        if cls._registered:
            return
        for module in cls.modules:
            cls.register_module(module)
        from .callable_wrappers import SorterWrapper, ComponentFormatter, EditorWrapper, FormatterWrapper
        for custom in SorterWrapper, ComponentFormatter, EditorWrapper, FormatterWrapper:
            cls.register_module(custom.Module)
        from . import datetime_overrides
        for key, val in cls.default_options.items():
            _Tabulator.defaultOptions[key] = val
        cls._registered = True
        _ignore_resize_observer_error()


    @staticmethod
    def register_module(module_name):
        if isinstance(module_name, str):
            if not module_name.endswith("Module"):
                module_name += "Module"
            module = _TabulatorModule[module_name]
        else:
            module = module_name
        _Tabulator.registerModule(module)

    def __new__(cls, **properties):
        cls._setup()
        return Tabulator5Template.__new__(cls, **properties)

    def __init__(self, **properties):
        self._t = None
        self._options = {}
        self._el = el = _get_dom_node(self)
        self._queued = []
        self._handlers = {}
        self.options = {}

        el.replaceChildren()

        props = _merge_from_default(_default_props, properties)
        self._options = _merge_from_default(_default_options, properties, row_formatter=self._row_formatter)
        self.init_components(**props)

    def _row_formatter(self, row):
        # because row_formatter is not a tabulator event but it is an anvil tabulator event
        self.raise_event("row_formatter", row=row)

    def _initialize(self):
        options = _camelKeys(self._options)
        data = options.pop("data", None)
        options["columns"] = [_camelKeys(defn) for defn in options["columns"]]
        options["columnDefaults"] = _camelKeys(options["columnDefaults"])
        options.update(_camelKeys(self.options))

        t = _Tabulator(self._el, self._options)
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

    def define(self, **options):
        if self._t is not None:
            msg = "define must be called before the Tabulator component is on the screen"
            raise RuntimeError(msg)
        options = map(lambda item: [_toCamel(item[0]), item[1]], options.items())
        self._options |= options

    data = _options_property("data", "getData", "setData")
    columns = _options_property("columns", None, "setColumns")
    column_defaults = _options_property("columnDefaults")

    border = _HtmlTemplate.border
    visible = _HtmlTemplate.visible
    role = _HtmlTemplate.role

    #### for the autocomplete
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
    "add_row", "delete_row", "update_row", "get_row", "select_row", "deselect_row", "get_selected_data", "add_data", "get_data",
    "update_or_add_data", "replace_data", "set_filter", "add_filter", "remove_filter", "get_filters", "clear_filter", "set_sort", "clear_sort"
)

for method in methods:
    delattr(Tabulator5, method)
