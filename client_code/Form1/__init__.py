from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    

  def primary_color_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.form2_1.add_row()

  def primary_color_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.form2_1.set_group_by('gender')

  def form2_1_row_click(self, **event_args):
    print(event_args['row'])






