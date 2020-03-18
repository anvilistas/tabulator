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
    self.columns_dropdown.items = [col['field'] for col in self.tabulator_1.columns]
    self.fields_dropdown.items = [col['field'] for col in self.tabulator_1.columns]
    

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.tabulator_1.data = anvil.server.call('get_list_data', n = 1000)
    

  def tabulator_1_row_click(self, **event_args):
    """This method is called when a row is clicked"""
    print(f"{event_args['event_name']}: {event_args['row']['id']}")

  def tabulator_1_row_selection_change(self, **event_args):
    print(f"{event_args['event_name']}: {len(event_args['rows'])} selected")
    if len(event_args['rows']):
      self.delete_selected.visible = True
    if len(event_args['rows']) == 1:
      self.edit_selected.visible = True

  def delete_selected_click(self, **event_args):
    """This method is called when the button is clicked"""
    index = self.tabulator_1.index
    indices = [row[index] for row in self.tabulator_1.get_selected()]
    
    self.tabulator_1.delete_row(indices)
    

  def edit_selected_click(self, **event_args):
    """This method is called when the button is clicked"""
    print(f'time to edit row: {self.tabulator_1.get_selected()}')

  def sort_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    col = self.columns_dropdown.selected_value
    asc = self.ascending_dropdown.selected_value
    self.tabulator_1.set_sort(col, asc)
    
    

  def filter_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    field = self.fields_dropdown.selected_value
    symbol = self.type_dropdown.selected_value
    value = self.value_box.text
    
    self.tabulator_1.set_filter(field, symbol, value)

  def reset_sort_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.tabulator_1.clear_sort()

  def reset_filter_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.tabulator_1.clear_filter()








