from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.tabulator_1.columns = [
      {'field': 'columnA', 'formatter': lambda row: Link(text=row['columnA'])},
      {'field': 'columnB', 'formatter': Link, 'formatterParams': {'text':'foo', 'icon': 'fa:bomb'}},
      {'field': 'columnC'},
      {'field': 'columnD'},
    ]
    
    self.tabulator_1.data = [{'id':0, 'columnA':'1', 'columnB':'2', 'columnC':'3', 'columnD':'4'},
                             {'id': 1, 'columnA':'2', 'columnB':'7', 'columnC':'4', 'columnD':'1'}
                            ]

    self.tabulator_1._table.addRow({'id': 2, 'columnA':'2', 'columnB':'7', 'columnC':'4', 'columnD':'1'})

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    print(self.tabulator_1.get_row(4))
    self.tabulator_1.add_row({'id': 3, 'columnA':'foo', 'columnB':'7', 'columnC':'4', 'columnD':'1'})

  def button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    print(self.tabulator_1.get_selected())
    self.tabulator_1.update_row(2, {'columnA': 'bar'})
    self.tabulator_1.select_row([1,2])
    print(self.tabulator_1._table.getRow(2).get('foo', 'blah'))

  def tabulator_1_row_click(self, row, **event_args):
    """This method is called when a row is clicked"""
    print(row)

  def tabulator_1_row_selected(self, row, **event_args):
    """This method is called when a row is selected"""
    print(row)

  def tabulator_1_row_selection_change(self, rows, **event_args):
    print(rows)

  def tabulator_1_cell_click(self, field, row, **event_args):
    """This method is called when a cell is clicked - event_args include field and row"""
    print(field, row)

  def tabulator_1_cell_edited(self, field, row, **event_args):
    """This method is called when a cell is edited - event_args include field and row"""
    print(field, row)










