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
            raise KeyError(f'you should provide an index for this row: {self._index}')
        self._data.append(row)
        js.call_js('add_row', self, row, top, pos)

    def select_row(self, row):
        js.call_js('select_row', self, row)

    def update_row(self, row):
        js.call_js('update_row', self, row.get(self._index), row)

    def set_group_by(self, field):
        js.call_js('set_group_by', self, field)
        
    def get_selected(self):
        js.call_js('get_selected', self)

    def add_data(self, data, top=False, pos=None):
      js.call_js('add_data', self, data,top, pos)
      self._data += data

      
    def update_or_add_data(self, data):
        js.call_js('update_or_add_row', self, data)
        for row in data:
            try:
                update_row = next(r for r in self._data if r.get(self.index, float('nan')) == row.get(self.index))
                update_row.update(row)
            except StopIteration as e:
                self._data.append(row)
    
    


# Events

      
    def row_selected(self, row):
        print('row selected')
        try:
            row = next(r for r in self._data if r.get(self.index, float('nan')) == row.get(self.index))
        except StopIteration as e:
            row = None
        self.raise_event('row_selected', row=row)

    def row_click(self, row):
        if isinstance(self._data, list):
            try:
                row = next(r for r in self._data if r.get(self.index, float('nan')) == row.get(self.index))
            except StopIteration as e:
                row = None
        elif isinstance(self._data, LiveObjectProxy):
            print(dir(self._data))
        self.raise_event('row_click', row=row)     

        
    def row_edited(self, js_row):
        if self._writeback:
            try:
                row = next(row for row in self._data if row.get(
                self.index, float('nan')) == js_row.get(self.index))
                row.update(js_row)
            except StopIteration as e:
                row = None
        else:
            row = js_row
        self.raise_event('row_edited', row=row)
        
        
    def row_selection_change(self, rows):
        selected_rows = []
        for row in rows:
            try:
                row = next(r for r in self._data if r.get(self.index, float('nan')) == row.get(self.index))
                selected_rows.append(row)
            except StopIteration as e:
                pass
        self.raise_event('row_selection_change', rows=selected_rows)

        
    def get_selected(self):
        rows = js.call_js('get_selected', self)
        selected_rows = []
        for row in rows:
            try:
                row = next(r for r in self._data if r.get(self.index, float('nan')) == row.get(self.index))
                selected_rows.append(row)
            except StopIteration as e:
                pass
        return selected_rows
      
         
# properties
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        js.call_js('set_data', self, self._data)

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
        print('setting columns')
        self._columns = value
        js.call_js('set_columns', self, self._columns, self._row_selectable=='checkbox')
            
    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

        
    @property
    def writeback(self):
        return self._writeback

    @index.setter
    def writeback(self, value):
        self._writeback = bool(value)

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



