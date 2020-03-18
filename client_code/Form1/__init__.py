from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    
    

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.tabulator_1.data = anvil.server.call('get_list_data', n = 5000)
    

  def tabulator_1_row_click(self, **event_args):
    """This method is called when a row is clicked"""
    print(f"{event_args['event_name']}: {event_args['row']['id']}")

  def tabulator_1_row_selection_change(self, **event_args):
    print(f"{event_args['event_name']}: {len(event_args['rows'])} selected")


