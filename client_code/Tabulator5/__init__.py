from ._anvil_designer import Tabulator5Template
from anvil.js import get_dom_node as _get_dom_node
from .utils import snake_to_camel as _toCamel

_event_call_signatures = {
    "rowClick": ("event", "row"),
    "cellClick": ("event", "cell"),
    "rowTap": ("event", "row"),
    "cellTap": ("event", "cell"),
    "cellEdited": ("cell",),
    "pageLoaded": ("pageno",),
    "rowSelected": ("row",),
    "rowDeselected": ("row",),
    "rowSelectetionChange": ("data", "rows"),
}

_default_options = {
    "auto_columns": False,
    "header_visible": True,
    "height": "",
    "index": "id",
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
    "align": "center",
    "headerSort": False,
    "cssClass": "title-center",
    "cellClick": lambda e, cell: cell.getRow().toggleSelect(),
}

class Tabulator5(Tabulator5Template):

    def __init__(self, **properties):
        self._t = None
        self._options = {"row_formatter": lambda row: self.raise_event("row_formatter", row=row)}
        self._el = _get_dom_node(self)
        self._queued = []
        self._handlers = {}

    def _initialize(self):
        data = self._options.pop("data")
        self._t = _Tabulator(self._el, self._options)
        for attr, args, kws in self._queued:
            getattr(self._t, attr)(*args, **kws)
        self._queued.clear()
        # use setData since initiating data
        # with anything other than list[dict] breaks tabulator
        self._t.setData(data)

    def _show(self, **event_args):
        if self._t is None:
            self._initialize()

    def __getattr__(self, attr):
        attr = _toCamel(attr)
        if self._t is None:
            return lambda *args, **kws: self._queued.append([attr, args, kws])
        return getattr(self._t, attr)

    def add_event_handler(self, event, handler):
        super().add_event_listener(event, handler)
        camel = _toCamel(event)
        call_sig = _event_call_signatures.get(camel)
        if call_sig is None:
            return
        def raiser(*args):
            kws = dict(zip(call_sig, args))
            return self.raise_event(event, **kws)
        self._handlers[handler] = raiser
        self.on(camel, raiser)

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
        return self._t.setData(value)

    @property
    def columns(self):
        if self._t is None:
            return self._options.get("columns")

    @columns.setter
    def columns(self, value):
        if self._t is None:
            self._options["columns"] = value
        return self._t.getColumnDefinitions()
