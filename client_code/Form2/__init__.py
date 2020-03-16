from ._anvil_designer import Form2Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

class Form2(Form2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    rows = anvil.server.call('get_table_search')
    self.tabulator_1.data = rows
    
    # Any code you write here will run when the form opens.
    

  def tabulator_1_row_click(self, **event_args):
    print(event_args['row'])

  def tabulator_1_row_edited(self, **event_args):
    """This method is called when a row is edited - returns the row - will edit the data inplace if writeback is set to True"""
    print(event_args['row'])

  def primary_color_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.tabulator_1.update_row({'id':4, 'name':'BoBo'})


  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
#     anvil.server.call_s('add_rows',100)
    pass







