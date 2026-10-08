# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from anvil import HtmlTemplate as _HtmlTemplate
from anvil.js import ProxyType as _ProxyType
from anvil.js import await_promise as _await_promise
from anvil.js import get_dom_node as _get_dom_node
from anvil.js import report_exceptions as _report_exceptions
from anvil.js.window import Object as _Object
from anvil.js.window import Promise as _Promise
from anvil.js.window import window as _window

from . import _datetime_overrides, _logger
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
    _normalizeColumns,
    _normalizeOptions,
    _options_property,
    _spacing_property,
    _to_module,
    _toCamel,
)
from ._js_tabulator import Tabulator as _Tabulator
from ._logger import logger

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

    @staticmethod
    def debug_logging(enable=True):
        _logger.debug_logging(enable)

    def __new__(cls, **properties):
        cls._setup()
        return TabulatorTemplate.__new__(cls, **properties)

    def __init__(self, **properties):
        logger.debug(f"__init__ called with properties={properties}")
        self._t = None
        self._live_reload_ready = False
        self._live_reload_initial_data = None
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
        logger.debug("Setup called")
        logger.debug(f"Default options: {cls.default_options}")
        for key, val in cls.default_options.items():
            _Tabulator.defaultOptions[key] = val
        if cls._registered:
            logger.debug("Setup: already completed, skipping setup")
            return
        _inject_theme(cls.theme)
        logger.debug(f"Injected theme: {cls.theme!r}")
        logger.debug("Registering modules")
        cls.register_module(cls.modules)
        logger.debug("Registering custom modules")
        cls.register_module(custom_modules)
        _datetime_overrides.init_overrides()
        logger.debug("Initialized datetime overrides")
        _ignore_resize_observer_error()
        logger.debug("Set up resize observer error handler")
        cls._registered = True

    @staticmethod
    def register_module(modules):
        if type(modules) not in (set, tuple, list):
            modules = [modules]
        modules = [_to_module(m) for m in modules]
        logger.debug(f"Calling Tabulator.registerModule with modules: {modules}")
        _Tabulator.registerModule(modules)

    # because row_formatter is not a tabulator event but it is an anvil tabulator event
    def _row_formatter(self, row):
        # Fix a bug where rowHeight was causing issues with scrolling
        rowHeight = row.getTable().options.get("rowHeight")
        if rowHeight:
            row.getElement().style.setProperty("height", f"{rowHeight}px")

        self.raise_event("row_formatter", row=row)

    def _initialize(self):
        logger.debug("Initializing tabulator")
        logger.debug(f"Options: {self.options}")

        options = _camelKeys(self._options) | _camelKeys(self.options)
        options = _normalizeOptions(options)
        options["columns"] = _normalizeColumns(options["columns"])
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
            and options.get("selectableRows") is None
        ):
            options["selectableRows"] = "highlight"

        # Tabulator mutates native row objects during editing. Snapshot the
        # constructor's dataset before handing it to JavaScript, in IDE runs
        # only; published tables do not pay for this extra copy.
        params = getattr(_window, "anvilParams", None)
        if params and getattr(params, "inIDE", False):
            try:
                self._live_reload_initial_data = _live_reload_copy(
                    options.get("data") or []
                )
            except TypeError:
                # Unsupported initial rows still render normally, but cannot
                # participate in portable reload state.
                self._live_reload_initial_data = None

        t = _Tabulator(self._dom_node, options)
        t.anvil_form = self
        self._t = t
        # Native initialized becomes true before initial data loading completes;
        # tableBuilt is the point at which a reload snapshot can read the rows.
        self._live_reload_ready = False

        def live_reload_ready(*args):
            self._live_reload_ready = True
            t.off("tableBuilt", live_reload_ready)

        t.on("tableBuilt", live_reload_ready)
        logger.debug("Tabulator initialized")

        for meth, event, handler in self._queued:
            logger.debug(f"Calling self.{meth}({event!r}, {handler})")
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

    @property
    def __anvil_live_reload_state__(self):
        """Experimental runtime snapshot; reading must not change the table."""
        t = self._t
        if not self._live_reload_ready or self._live_reload_initial_data is None:
            return None
        if not _live_reload_uses_local_data(t):
            return None
        return {
            "initial_data": self._live_reload_initial_data,
            "data": _live_reload_copy(t.getData()),
            "sorters": [{"column": s.field, "dir": s.dir} for s in t.getSorters()],
            "selected": [
                _live_reload_copy(row.getIndex()) for row in t.getSelectedRows()
            ],
            "page": t.getPage() if t.options.pagination else None,
        }

    @__anvil_live_reload_state__.setter
    def __anvil_live_reload_state__(self, state):
        if state is None:
            return
        if self._t is None:
            self.remove_event_handler("show", self._show)
            self._initialize()
        t = self._t
        if not self._live_reload_ready:

            def wait_for_build(resolve, reject):
                def built(*args):
                    t.off("tableBuilt", built)
                    resolve(None)

                t.on("tableBuilt", built)

            _await_promise(_Promise(wait_for_build))
        # A constructor can switch the replacement to a source-backed table.
        # Its loader owns that data; never replace it with the old local rows.
        if not _live_reload_uses_local_data(t):
            return
        # New constructor data takes effect. Only retain edited rows while the
        # constructor's dataset is unchanged, as with a column/title edit.
        if (
            self._live_reload_initial_data is not None
            and self._live_reload_initial_data == state.get("initial_data")
        ):
            _await_promise(t.setData(state["data"]))
        t.setSort(state["sorters"])
        t.deselectRow()
        t.selectRow(state["selected"])
        if state["page"] is not None and t.options.pagination:
            # Changed constructor data can have fewer pages than the old table.
            _await_promise(t.setPage(min(state["page"], t.getPageMax())))

    def __anvil_live_reload_dispose__(self):
        """Called for retired replacements, never for cached hide/show."""
        if self._t is not None:
            self._t.destroy()
            self._t = None

    data = _options_property("data", "getData", "setData")

    @property
    def columns(self):
        return self._options.get("columns")

    @columns.setter
    def columns(self, value):
        self._options["columns"] = value
        if self._t is None:
            return
        self._t.setColumns(_normalizeColumns(value))

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
            logger.debug(f"not initialized, queuing self.{meth}({event!r}, {handler})")
            self._queued.append([meth, _toCamel(event), handler])
        else:
            logger.debug(f"initialized, calling self.{meth}({event!r}, {handler})")
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


def _live_reload_uses_local_data(table):
    # Ajax is optional in the core build; its getter exists only when registered.
    get_ajax_url = getattr(table, "getAjaxUrl", None)
    return not (
        (get_ajax_url is not None and get_ajax_url())
        or table.options.get("appTable") is not None
        or table.options.get("useModel")
        or any(
            table.options.get(mode) == "remote"
            for mode in ("paginationMode", "sortMode", "filterMode")
        )
    )


def _live_reload_copy(value):
    """Copy supported local row data without retaining JavaScript proxies."""
    if value is None or type(value) in (str, bool, int, float):
        return value
    if type(value) is dict:
        return {key: _live_reload_copy(item) for key, item in value.items()}
    # Native arrays are ProxyList instances, which inherit Python list.
    if isinstance(value, (list, tuple)):
        return [_live_reload_copy(item) for item in value]
    if (
        isinstance(value, _ProxyType)
        and _Object.getPrototypeOf(value) == _Object.prototype
    ):
        return {key: _live_reload_copy(item) for key, item in dict(value).items()}
    raise TypeError("Tabulator live reload supports only plain local row data")
