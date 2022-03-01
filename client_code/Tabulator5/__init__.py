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
    def add_row(self, row, top=True, pos=None):
        """add a row - ensure the row has an index"""
        index = row.get(self._index)
        if index is None:
            raise KeyError(f"you should provide an index '{self._index}' for this row")
        if self.get_row(index):
            raise KeyError(f"The index '{self._index}' should be unique")

        self._table.addRow(row, top, pos)

    def delete_row(self, index):
        """delete a row - the index of the row must be provided"""
        self._table.deleteRow(index)

    def update_row(self, index, row):
        """update a row - the index of the row must be provided"""
        try:
            self._table.updateRow(index, row)
        except Exception as e:
            if "NotFoundError" in repr(e):
                pass
            else:
                raise e

    def get_row(self, index):
        """get the row - the index of the row must be provided"""
        row = self._table.getRow(index)
        return dict(row.getData()) if row else None

    def select_row(self, index_or_indexes):
        self._table.selectRow(index_or_indexes)

    def deselect_row(self, index_or_indexes=None):
        """deselect a row (single index), rows (list of indexes) or all rows (no argument)"""
        if index_or_indexes is None:
            self._table.deselectRow()  # call it with an empty argument
        else:
            self._table.deselectRow(index_or_indexes)

    def get_selected(self):
        """returns a list of selected rows"""
        return [dict(row) for row in self._table.getSelectedData()]

    def add_data(self, data, top=False, pos=None):
        """add data - use the keyword arguments to determine where in the table it gets added"""
        self._table.addData(data, top, pos)

    def update_or_add_data(self, data):
        """checks each row and updates data if the row exists, otherwise creates a new row"""
        self._table.updateOrAddData(data)

    @maintain_scroll_position
    def replace_data(self, data):
        # useful to keep the datatable in the same place
        """replace all data in the table"""
        self._table.replaceData(data)

    def set_filter(self, field, type=None, value=None):
        """for multiple filters pass a list of dicts with keys 'field', 'type', 'value'"""
        if callable(field):
            filter_func = field
            field = lambda data, params: filter_func(dict(data), **params)
        self._table.setFilter(field, type, value)

    def add_filter(self, field, type=None, value=None):
        if callable(field):
            filter_func = field
            field = lambda data, params: filter_func(dict(data), **params)
        self._table.addFilter(field, type, value)

    def remove_filter(self, field=None, type=None, value=None):
        self._table.removeFilter(field, type, value)

    def get_filters(self):
        return self._table.getFilters()

    def clear_filter(self, *args):
        """include an arg of True to clear header filters as well"""
        self._table.clearFilter(*args)

    def set_sort(self, column, ascending=True):
        """first argument can also be a list of sorters [{'column':'name', 'ascending':True}]"""
        if isinstance(column, list):
            sorters = column
            for sorter in sorters:
                sorter["dir"] = "asc" if sorter.pop("ascending") else "desc"
            self._table.setSort(sorters)
        elif isinstance(column, str):
            self._table.setSort(column, "asc" if ascending else "desc")
        else:
            raise TypeError(
                "expected first argument to be a list of sorters or the column field name"
            )

    def clear_sort(self):
        self._table.clearSort()
        # reset the table data
        debugger
        data = self._table.getData()
        self._table.setData(data)