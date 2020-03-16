from ._anvil_designer import TabulatorTemplate
from anvil import *

"""
    autoColumns:true,
    columnHeaderVertAlign: top, *middle, bottom
    groupBy: None;
    setGroupBy
    paginationSizeSelector
    index
    
height	string/int	false	Sets the height of the containing element, can be set to any valid height css value. If set to false (the default), the height of the table will resize to fit the table data.	
virtualDom	boolean	true	Enable rendering using the Virtual DOM engine	 Explore
virtualDomBuffer	integer	false	Manually set the size of the virtual DOM buffer	 Explore
placeholder	string/DOM Node	""	placeholder element to display on empty table	 Explore
footerElement	string/DOM Node	(see documentation)	Footer element for the table	 Explore
tooltips	boolean/function	false	Function to generate tooltips for cells	 Explore
tooltipGenerationMode	string	"load"	When to regenerate cell tooltip value	 Explore
history	boolean/function	false	Enable user interaction history functionality	 Explore
keybindings	boolean/function	false	Keybinding configuration object	 Explore
locale	string/boolean	false	set the current localization language	 Explore
langs	object	(see documentation)	hold localization templates	 Explore
downloadDataFormatter	function	false	callback function to alter table data before download	 Explore
downloadConfig	object	object	choose which parts of the table are included in downloaded files	 Explore
htmlOutputConfig	object	object	choose which parts of the table are included in getHtml function output	 Explore
reactiveData	boolean	false	enable data reactivity	 Explore
tabEndNewRow	boolean/object/function	false	add new row when user tabs of the end of the table	 Explore
invalidOptionWarnings	boolean	true	show console warnings if invalid options are used

"""


class Tabulator(TabulatorTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    print(dir(self))
    js.call_js('create_table',
                self,
                self._auto_columns,
                self._header_align,
                self._header_visible,
                self._index,
                self._layout,
                self._moveable_columns,
                self._pagination,
                self._pagination_button_count,
                self._pagination_size,
                self._pagination_size_selector,
                self._resizable_columns,
                self._row_selectable
              ) 
    # Any code you write here will run when the form opens.
    
    def add_row(self, row={}, top=True, pos=None):
        self._data.append(row)
        js.call_js('add_row', self, row, top, pos)

    def select_row(self, row):
        pass

    def update_row(self, row):
        pass


    def set_group_by(self, field):
        js.call_js('set_group_by', self, field)

        
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
    def moveable_columns(self):
        return self._moveable_columns

    @moveable_columns.setter
    def moveable_columns(self, value):
        self._moveable_columns = bool(value)

    @property
    def header_align(self):
        return self._header_align

    @header_align.setter
    def header_align(self, value):
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
        self._pagination = bool(value)

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
        self._row_selectable = bool(value)

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
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        print('setting columns')
        self._columns = value
        js.call_js('set_columns', self, self._columns)

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
        self._height = value
        if self.parent:
            js.call_js('set_height', self, value)

    def row_selected(self, row):
        try:
            row = next(r for r in self._data if r.get(
                self.index, float('nan')) == row.get(self.index))
        except StopIteration as e:
            row = None
        self.raise_event('row_selected', row=row)

    def row_click(self, row):
        try:
            row = next(r for r in self._data if r.get(
                self.index, float('nan')) == row.get(self.index))
        except StopIteration as e:
            row = None
        self.raise_event('row_click', row=row)

    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        js.call_js('redraw', self)
        raise_event('show')


    def row_edited(self, js_row):
        if writeback:
            try:
                row = next(row for row in self._data if row.get(
                self.index, float('nan')) == js_row.get(self.index))
                row.update(js_row)
            except StopIteration as e:
                row = None
        else:
            row = js_row
        raise_event('row_edited', row=row)

    