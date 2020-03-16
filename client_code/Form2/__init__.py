from ._anvil_designer import Form2Template
from anvil import *

class Form2(Form2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    

  def tabulator_1_row_click(self, **event_args):
    print(event_args['row'])

