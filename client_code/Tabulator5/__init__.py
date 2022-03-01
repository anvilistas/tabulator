from ._anvil_designer import Tabulator5Template
from anvil.js import get_dom_node as _get_dom_node
from .utils import _toCamel, _merge_from_default
from . import setup as _setup
from .js_tabulator import Tabulator as _Tabulator
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


class Tabulator5(Tabulator5Template):

    def __init__(self, **properties):
        self._t = None
        self._options = {}
        self._el = el = _get_dom_node(self)
        self._queued = []
        self._handlers = {}

        el.replaceChildren()

        props = _merge_from_default(_default_props, properties)
        options = _merge_from_default(_default_options, properties)
        self.init_components(**props)
        self.define(row_formatter=self._row_formatter, **options)

    def _row_formatter(self):
        # because row_formatter is not a tabulator event but it is an anvil tabulator event
        self.raise_event("row_formatter", row=row)

    def _initialize(self):
        data = self._options.pop("data")
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
        self._handlers[handler] = raiser
        self.on(_toCamel(event), raiser)

    set_event_handler = add_event_handler

    def remove_event_handler(self, event, handler):
        super().remove_event_handler(event, handler)
        self.off(_toCamel(event), self._handlers.get(handler))

    def define(self, **options):
        if self._t is not None:
            msg = "define must be called before the Tabulator component is on the screen"
            raise RuntimeError(msg)
        options = map(lambda item: [_toCamel(item[0]), item[1]], options.items())
        self._options |= options

    @property
    def data(self):
        if self._t is None:
            return self._options.get("data")
        return self._t.getData()

    @data.setter
    def data(self, value):
        # check the type of the value
        if self._t is None:
            self._options["data"] = value
        else:
            return self._t.setData(value)

    @property
    def columns(self):
        return self._options.get("columns")

    @columns.setter
    def columns(self, value):
        self._options["columns"] = value
        if self._t is not None:
            return self._t.setColumns(value)

    border = _HtmlTemplate.border
    visible = _HtmlTemplate.visible
    role = _HtmlTemplate.role
    
    #### for the autocomplete
    