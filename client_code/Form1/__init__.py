from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
    
#     self.tabulator_1.data = [{'columnA':'1', 'columnB':'2', 'columnC':'3', 'columnD':'4'},
#                    {'columnA':'2', 'columnB':'7', 'columnC':'4', 'columnD':'1'}],


    self.tabulator_1.table.addRow({'columnA':'2', 'columnB':'7', 'columnC':'4', 'columnD':'1'})

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    print(self.tabulator_1.get_row(4))
    
    self.tabulator_1.add_row({'id': 2, 'columnA':'foo', 'columnB':'7', 'columnC':'4', 'columnD':'1'})

  def button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    print(self.tabulator_1.get_selected())
    self.tabulator_1.update_row(2, {'columnA': 'bar'})
    self.tabulator_1.select_row([1,2])
    print(self.tabulator_1.table.getRow(2).get('foo', 'blah'))


