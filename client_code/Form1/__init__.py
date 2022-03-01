from ._anvil_designer import Form1Template
from anvil import *
from datetime import date
from ..Tabulator5 import row_selection_column

def c(cell):
    debugger;
    print("huh")

columns = [
    row_selection_column,
    {"title": "Name", "field": "name", "width": 150, "accessor": "roundDown"},
    {
        "title": "Age",
        "field": "age",
        "hozAlign": "left",
        "formatter": "progress",
    },
    {"title": "Favourite Color", "field": "col", "editor": True},
    {
        "title": "Date Of Birth",
        "field": "dob",
        "sorter": "date",
        "formatter": "date",
        "hozAlign": "center",
        "formatterParams": {"format": "%d/%m/%Y"},
        "editor": "date",
        "cellEditCancelled": c,
    },
]

tabledata = [
    {"id": 1, "name": "Oli Bob", "age": "12", "col": "red", "dob": date(1982, 5, 14)},
    {"id": 2, "name": "Mary May", "age": "1", "col": "blue", "dob": date(1982, 5, 14)},
    {
        "id": 3,
        "name": "Christine Lobowski",
        "age": "42",
        "col": "green",
        "dob": date(1982, 5, 22),
    },
    {
        "id": 4,
        "name": "Brendon Philips",
        "age": "125",
        "col": "orange",
        "dob": date(1980, 8, 1),
    },
    {
        "id": 5,
        "name": "Margret Marmajuke",
        "age": "16",
        "col": "yellow",
        "dob": date(1999, 1, 31),
    },
]


class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.tabulator5_1.data = tabledata
        self.tabulator5_1.columns = columns
        self.tabulator5_1.define(pagination_size_selector = [1, 2, 5, 10])
        # Any code you write here will run when the form opens.

    def tabulator5_1_row_click(self, **event_args):
        print("click", event_args)

    def tabulator5_1_cell_click(self, **event_args):
        print("cell click", event_args)

    def form_refreshing_data_bindings(self, **event_args):
        """This method is called when refreshing_data_bindings is called"""
        pass

    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        from time import sleep
        sleep(2)
        print(self.tabulator5_1.columns)

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.tabulator5_1.parent is None:
            self.add_component(self.tabulator5_1)
        else:
            self.tabulator5_1.remove_from_parent()







