from ._anvil_designer import TabulatorTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class Tabulator(TabulatorTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        js.call_js('create_table',
                    self,
                    self._auto_columns,
                    self._header_align,
                    self._header_visible,
                    self._height,
                    self._index,
                    self._layout,
                    self._movable_columns,
                    self._pagination,
                    self._pagination_button_count,
                    self._pagination_size,
                    self._pagination_size_selector,
                    self._resizable_columns,
                    'highlight' if self._row_selectable == 'checkbox' else self._row_selectable
                    )
        # Any code you write here will run when the form opens.

# Methods
    def add_row(self, row={}, top=True, pos=None):
        if not row.get(self._index):
            raise KeyError(f"you should provide an index '{self._index}' for this row")
        if js.call_js('get_row', row.get(self._index)):
            raise KeyError(f"The index '{self._index}' should be unique")
        js.call_js('add_row', self, row, top, pos)
        self.data = js.call_js('get_data', self)
    
    def delete_row(self, index):
        js.call_js('delete_row', self, index)
        self.data = js.call_js('get_data', self)

    def update_row(self, index, row):
        js.call_js('update_row', self, index, row)
        self.data = js.call_js('get_data', self)
        
    def get_row(self, index):
        row = js.call_js('get_row', index)
        return row
        
    def select_row(self, row):
        js.call_js('select_row', self, row)
     
    def get_selected(self):
        return js.call_js('get_selected', self)

    def add_data(self, data, top=False, pos=None):
        js.call_js('add_data', self, data, top, pos)
        self.data = js.call_js('get_data', self)

    def update_or_add_data(self, data):
        js.call_js('update_or_add_row', self, data)
        self.data = js.call_js('get_data', self)
    
    def set_filter(self, field, type=None, value=None):
        """for multiple filters pass a list of dicts with keys 'field', 'type', 'value'"""
        js.call_js('set_filter', self, field, type, value)
        
    def add_filter(self, field, type, value):
        js.call_js('add_filter', self, field, type, value)
        
    def remove_filter(self, field, type, value):
        js.call_js('remove_filter', self, field, type, value)
        
    def get_filters(self):
        return js.call_js('get_filter', self)
      
    def clear_filter(self, *args):
        """include an arg of True to clear header filters as well"""
        js.call_js('clear_filter', self, *args)
        
    def set_sort(self, column, ascending=True):
        """first argument can also be a list of sorters [{'column':'name', 'ascending':True}]"""
        if isinstance(column, list):
            sorters = column
            for sorter in sorters:
                sorter['dir'] = 'asc' if sorter.pop('ascending') else 'desc'
            js.call_js('set_sort', self, sorters)
        elif isinstance(column, str):
            js.call_js('set_sort', self, column, 'asc' if ascending else 'desc')
        else:
            raise TypeError('expected first argument to be a list of sorters or the column field name')
    
    def clear_sort(self):
        js.call_js('clear_sort', self)
        
    def set_group_by(self, field):
        js.call_js('set_group_by', self, field)
   

# Events
    def row_selected(self, row):
        self.raise_event('row_selected', row=row)

    def row_click(self, row):
        self.raise_event('row_click', row=row)     

    def row_edited(self, row):
        self.data = js.call_js('get_data', self)
        self.raise_event('row_edited', row=row)
        
    def row_selection_change(self, rows):
        self.raise_event('row_selection_change', rows=rows)
        
    def get_selected(self):
        rows = js.call_js('get_selected', self)
        return rows
      
      
# properties
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        js.call_js('set_data', self, value)
        self._data = js.call_js('get_data', self)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value.isdigit():
          value = value+'px'
        self._height = value
        if self.parent:
            js.call_js('set_height', self, value)

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value
        js.call_js('set_columns', self, self._columns, self._row_selectable=='checkbox')
            
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
        if value not in ('top', 'middle', 'bottom'):
            value = 'middle'
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
        if value:
          value = 'local'
        self._pagination = value

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
        if value == 'None' or not value:
            self._pagination_size_selector = None
        else:
            value = value.replace(',', ' ')
            self._pagination_size_selector = [int(i) for i in value.split()]

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        layouts = ('fitData', 'fitDataFill', 'fitDataStretch', 'fitColumns')
        if value not in layouts:
            value = 'fitColumns'
        self._layout = value

        
    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        js.call_js('redraw', self)



