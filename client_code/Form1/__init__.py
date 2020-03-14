from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
#     self.form2_1.height = 800
#     self.form2_1.data = [
#     {'id':1, 'name':"Oli baba", 'progress':12, 'gender':"male", 'rating':1, 'col':"red" },
#     {'id':2, 'name':"Mary May", 'progress':1, 'gender':"female", 'rating':2, 'col':"blue" },
#     {'id':3, 'name':"Christine Lobowski", 'progress':42, 'gender':"female", 'rating':0, 'col':"green" },
#     {'id':4, 'name':"Brendon Philips", 'progress':100, 'gender':"male", 'rating':1, 'col':"orange" },
#     {'id':5, 'name':"Margret Marmajuke", 'progress':16, 'gender':"female", 'rating':5, 'col':"yellow"},
# ];
    pass

  def form2_1_row_click(self, **event_args):
    print(event_args)
    print(event_args['row'])
    



