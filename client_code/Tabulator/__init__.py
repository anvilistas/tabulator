"""
    Tabulator for Anvil
    an anvil wrapper for tabulator: https://github.com/olifolkerd/tabulator
    Copyright 2020 Stu Cork

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Source code published at https://github.com/s-cork/Tabulator
"""

from ._anvil_designer import TabulatorTemplate
from anvil.js.window import Tabulator as _Tabulator
from anvil.js import get_dom_node as _get_dom_node

from ._Helpers import maintain_scroll_position
from ._CleanCols import _clean_cols, _clean_editor, _clean_formatter, _clean_sorter

from anvil import HtmlTemplate as _HtmlTemplate

class Tabulator(TabulatorTemplate):
    def __init__(self, **properties):
        # allow Tabulator to be set in code with default values
        self._from_cache = False
        self._table_init = False

        el = self._el = _get_dom_node(self)
        properties = {
            "auto_columns": None,
            "header_align": "middle",
            "header_visible": True,
            "height": "",
            "index": "id",
            "layout": "fitColumns",
            "movable_columns": False,
            "pagination": True,
            "pagination_button_count": 5,
            "pagination_size": 10,
            "pagination_size_selector": "6 10 20",
            "resizable_columns": True,
            "row_selectable": "checkbox",
            "spacing_above": "small",
            "spacing_below": "small",
            "border": "",
            "visible": True,
        } | properties
        
        self.init_components(**properties)

        row_selectable = self._row_selectable
        
        self._table = _Tabulator(
            el,
            {
                "autoColumns": self._auto_columns,
                "headerAlign": self._header_align,
                "headerVisible": self._header_visible,
                "height": self._height,
                "index": self._index,
                "layout": self._layout,
                "moveableColumns": self._resizable_columns,
                "pagination": self._pagination,
                "paginationButtonCount": self._pagination_button_count,
                "paginationSize": self._pagination_size,
                "paginationSizeSelector": self._pagination_size_selector,
                "resizableColumns": self._resizable_columns,
                "selectable": "highlight" if row_selectable == "checkbox" else row_selectable,
                "rowSelected": self.row_selected,
                "rowClick": self.row_click,
                "cellEdited": self.cell_edited,
                "rowSelectionChanged": self.row_selection_change,
                "cellClick": self.cell_click,
                "pageLoaded": self.page_loaded,
            },
        )

        self.columns = properties.get("columns", [])
        self._table_init = True
        self.visible = self.visible

    # helpers
    _clean_cols = _clean_cols
    _clean_editor = _clean_editor
    _clean_formatter = _clean_formatter
    _clean_sorter = _clean_sorter

    # Methods
    def add_row(self, row, top=True, pos=None):
        """add a row - ensure the row has an index"""
        index = row.get(self._index)
        if index is None:
            raise KeyError(f"you should provide an index '{self._index}' for this row")
        if self.get_row(index):
            raise KeyError(f"The index '{self._index}' should be unique")

        self._table.addRow(row, top, pos)

    def delete_row(self, index):
        self._table.deleteRow(index)

    def update_row(self, index, row):
        try:
            self._table.updateRow(index, row)
        except Exception as e:
            if "NotFoundError" in repr(e):
                pass
            else:
                raise e

    def get_row(self, index):
        row = self._table.getRow(index)
        return dict(row.getData()) if row else None

    def select_row(self, index_or_indexes):
        self._table.selectRow(index_or_indexes)

    def deselect_row(self, index_or_indexes=None):
        if index_or_indexes is None:
          self._table.deselectRow() # call it with an empty argument
        else:
          self._table.deselectRow(index_or_indexes)

    def get_selected(self):
        return [dict(row) for row in self._table.getSelectedData()]

    def add_data(self, data, top=False, pos=None):
        self._table.addData(data, top, pos)

    def update_or_add_data(self, data):
        self._table.updateOrAddData(data)

    @maintain_scroll_position
    def replace_data(self, data):
        # useful to keep the datatable in the same place
        self._table.replaceData(data)

    def set_filter(self, field, type=None, value=None):
        """for multiple filters pass a list of dicts with keys 'field', 'type', 'value'"""
        if callable(field):
            filter_func = field
            field = lambda data, params: filter_func(dict(data), **params)
        self._table.setFilter(field, type, value)

    def add_filter(self, field, type, value):
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
            raise TypeError("expected first argument to be a list of sorters or the column field name")

    def clear_sort(self):
        self._table.clearSort()
        # reset the table data
        self._table.setData(self._table.getData())

    def set_group_by(self, field):
        self._table.setGroupBy(field)

    # Events
    def row_selected(self, row):
        return self.raise_event("row_selected", row=dict(row.getData()))

    def row_click(self, e, row):
        return self.raise_event("row_click", row=dict(row.getData()))

    def row_selection_change(self, e, rows):
        return self.raise_event("row_selection_change", rows=[dict(row.getData()) for row in rows])

    def cell_click(self, e, cell):
        self.raise_event("cell_click", field=cell.getField(), row=dict(cell.getData()))

    def page_loaded(self, pageno):
        self.raise_event("page_loaded", pageno=pageno)    
    
    def cell_edited(self, cell):
        return self.raise_event("cell_edited", field=cell.getField(), row=dict(cell.getData()))

    @maintain_scroll_position
    def redraw(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        # redraw on show
        self._table.redraw()

    def form_show(self, **event_args):
        #         if not self._from_cache:
        self.redraw()
        self._from_cache = True

    # properties
    @property
    def data(self):
        return [dict(row) for row in self._table.getData()]

    @data.setter
    def data(self, value):
        self._table.setData(value)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        if value.isdigit():
            value = value + "px"
        if self.parent:
            self._table.setHeight(value)

    @property
    def columns(self):
        return self._columns or []

    @columns.setter
    def columns(self, value):
        self._columns = value
        cols = self._clean_cols(value)
        self._table.setColumns(cols)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def auto_columns(self):
        return self._auto_columns

    @auto_columns.setter
    def auto_columns(self, value):
        self._auto_columns = bool(value)

    @property
    def resizable_columns(self):
        return self._resizable_columns

    @resizable_columns.setter
    def resizable_columns(self, value):
        self._resizable_columns = bool(value)

    @property
    def movable_columns(self):
        return self._movable_columns

    @movable_columns.setter
    def movable_columns(self, value):
        self._movable_columns = bool(value)

    @property
    def header_align(self):
        return self._header_align

    @header_align.setter
    def header_align(self, value):
        value = value.strip().lower()
        if value not in ("top", "middle", "bottom"):
            value = "middle"
        self._header_align = value

    @property
    def header_visible(self):
        return self._header_visible

    @header_visible.setter
    def header_visible(self, value):
        self._header_visible = bool(value)

    @property
    def pagination(self):
        return self._pagination

    @pagination.setter
    def pagination(self, value):
        self._pagination = "local" if value else value

    @property
    def pagination_size(self):
        return self._pagination_size

    @pagination_size.setter
    def pagination_size(self, value):
        self._pagination_size = int(value)

    @property
    def pagination_button_count(self):
        return self._pagination_button_count

    @pagination_button_count.setter
    def pagination_button_count(self, value):
        self._pagination_button_count = int(value)

    @property
    def row_selectable(self):
        return self._row_selectable

    @row_selectable.setter
    def row_selectable(self, value):
        """true, false, checkbox, highlight"""
        self._row_selectable = value

    @property
    def pagination_size_selector(self):
        return self._pagination_size_selector

    @pagination_size_selector.setter
    def pagination_size_selector(self, value):
        value = value.strip()
        if value == "None" or not value:
            self._pagination_size_selector = None
        else:
            value = value.replace(",", " ")
            self._pagination_size_selector = [int(i) for i in value.split()]

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        layouts = ("fitData", "fitDataFill", "fitDataStretch", "fitColumns")
        if value not in layouts:
            value = "fitColumns"
        self._layout = value

    @property
    def spacing_above(self):
        return self._spacing_above

    @spacing_above.setter
    def spacing_above(self, value):
        self._spacing_above = value
        self._el.classList.add("anvil-spacing-above-" + self._spacing_above)

    @property
    def spacing_below(self):
        return self._spacing_below

    @spacing_below.setter
    def spacing_below(self, value):
        self._spacing_below = value
        self._el.classList.add("anvil-spacing-below-" + self._spacing_below)
    
    border = _HtmlTemplate.border
    visible = _HtmlTemplate.visible
