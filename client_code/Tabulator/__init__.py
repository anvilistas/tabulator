from ._anvil_designer import TabulatorTemplate
import anvil


class Tabulator(TabulatorTemplate):
    def __init__(self, **properties):
        # allow Tabulator to be set in code with default values
        defaults = {'auto_columns': None, 
                    'header_align': 'middle', 
                    'header_visible': True, 
                    'height': '', 
                    'index': 'id', 
                    'layout': 'fitColumns', 
                    'movable_columns': False, 
                    'pagination': True, 
                    'pagination_button_count': 5, 
                    'pagination_size': 10,
                    'pagination_size_selector': '6 10 20', 
                    'resizable_columns': True, 
                    'row_selectable': 'checkbox',
                    'spacing_above': 'small', 
                    'spacing_below': 'small', 
                   }

        defaults.update(properties)
        
        self.init_components(**defaults)
        anvil.js.call_js('create_table',
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
                    'highlight' if self._row_selectable == 'checkbox' else self._row_selectable,
                    self._spacing_above,
                    self._spacing_below,
                    )
        self._data = []
        


# Methods
    def add_row(self, row, top=True, pos=None):
        if row.get(self._index) is None:
            raise KeyError(f"you should provide an index '{self._index}' for this row")
        if anvil.js.call_js('get_row', self, row.get(self._index)):
            raise KeyError(f"The index '{self._index}' should be unique")
        anvil.js.call_js('add_row', self, row, top, pos)
        
        self._data = anvil.js.call_js('get_data', self)
    
    def delete_row(self, index):
        anvil.js.call_js('delete_row', self, index)
        self._data = anvil.js.call_js('get_data', self)

    def update_row(self, index, row):
        anvil.js.call_js('update_row', self, index, row)
        self._data = anvil.js.call_js('get_data', self)
        
    def get_row(self, index):
        row = anvil.js.call_js('get_row', self, index)
        return row
        
    def select_row(self, row):
        anvil.js.call_js('select_row', self, row)
     
    def get_selected(self):
        return anvil.js.call_js('get_selected', self)
      
    def add_data(self, data, top=False, pos=None):
        anvil.js.call_js('add_data', self, data, top, pos)
        self._data = anvil.js.call_js('get_data', self)

    def update_or_add_data(self, data):
        anvil.js.call_js('update_or_add_row', self, data)
        self._data = anvil.js.call_js('get_data', self)

    def replace_data(self, data):
        # useful to keep the datatable in the same place
        anvil.js.call_js('replace_data', self, data)
        self._data = anvil.js.call_js('get_data', self)

    def set_filter(self, field, type=None, value=None):
        """for multiple filters pass a list of dicts with keys 'field', 'type', 'value'"""
        anvil.js.call_js('set_filter', self, field, type, value)
        
    def add_filter(self, field, type, value):
        anvil.js.call_js('add_filter', self, field, type, value)
        
    def remove_filter(self, field=None, type=None, value=None):
        anvil.js.call_js('remove_filter', self, field, type, value)
        
    def get_filters(self):
        return anvil.js.call_js('get_filters', self)
      
    def clear_filter(self, *args):
        """include an arg of True to clear header filters as well"""
        anvil.js.call_js('clear_filter', self, *args)
        
    def set_sort(self, column, ascending=True):
        """first argument can also be a list of sorters [{'column':'name', 'ascending':True}]"""
        if isinstance(column, list):
            sorters = column
            for sorter in sorters:
                sorter['dir'] = 'asc' if sorter.pop('ascending') else 'desc'
            anvil.js.call_js('set_sort', self, sorters)
        elif isinstance(column, str):
            anvil.js.call_js('set_sort', self, column, 'asc' if ascending else 'desc')
        else:
            raise TypeError('expected first argument to be a list of sorters or the column field name')
    
    def clear_sort(self):
        anvil.js.call_js('clear_sort', self)
        
    def set_group_by(self, field):
        anvil.js.call_js('set_group_by', self, field)
   

# Events
    def row_selected(self, row):
        self.raise_event('row_selected', row=row)

    def row_click(self, row):
        self.raise_event('row_click', row=row)     
        
    def row_selection_change(self, rows):
        self.raise_event('row_selection_change', rows=rows)
        
    def get_selected(self):
        rows = anvil.js.call_js('get_selected', self)
        return rows
      
    def cell_click(self, field, row):
        self.raise_event('cell_click', field=field, row=row)
        
    def cell_edited(self, field, row):
        self._data = anvil.js.call_js('get_data', self)
        self.raise_event('cell_edited', field=field, row=row)
 
    def redraw(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        # redraw on show
        anvil.js.call_js('redraw', self)
      
# properties
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        anvil.js.call_js('set_data', self, value)
        self._data = anvil.js.call_js('get_data', self)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        if value.isdigit():
            value = value+'px'
        if self.parent:
            anvil.js.call_js('set_height', self, value)

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value
        anvil.js.call_js('set_columns', self, self._columns, self._row_selectable=='checkbox')
            
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
    
    @property
    def spacing_above(self):
        return self._spacing_above
      
    @spacing_above.setter
    def spacing_above(self, value):
        self._spacing_above = value
      
    @property
    def spacing_below(self):
        return self._spacing_below
      
    @spacing_below.setter
    def spacing_below(self, value):
        self._spacing_below = value

        

# private methods
    def _render_cell(self, function_or_component, row, params):
        pass

    def _render_cell_with_component(self, component, properties):
        component = component(**properties)
        return component
