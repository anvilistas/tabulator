from ._anvil_designer import TabulatorTemplate
from anvil import *


class Tabulator(TabulatorTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self._uid = js.call_js('create_table', self, self._height, self._layout)
    print(self._uid)
    # Any code you write here will run when the form opens.
    
  
  @property
  def layout(self):
    return self._layout
  
  @layout.setter
  def layout(self, value):
    layouts = ('fitData', 'fitDataFill', 'fitDataStretch','fitColumns')
    if value not in layouts:
      raise ValueError(f"layout must be one of: {', '.join(layouts)}")
    self._layout = value

  @property
  def columns(self):
    return self._columns

  @columns.setter
  def columns(self, value):
    print('setting columns')
    self._columns = value
    js.call_js('set_columns', self._uid, self._columns)
    
  
  @property
  def data(self):
    return self._data

  @data.setter
  def data(self, value):
    print('setting data')
    self._data = value
    js.call_js('set_data', self._uid, self._data)
  
  @property
  def height(self):
    return self._height
  
  @height.setter
  def height(self, value):
    self._height = value
    if self.parent:
      js.call_js('set_height', self._uid, value)

  def row_selected(self, row):
    print(row)
    

  def row_click(self, row):
    for data in self._data:
      if all(row[v] == data[v] for v in data):
        break
    else:
      return
    print(row)
    print(data)
    self.raise_event('row_click', row=data)     
   
    
  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    js.call_js('setup_table', self._uid)

    