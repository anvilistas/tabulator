# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from datetime import date

from anvil import *

from ..Tabulator5 import row_selection_column
from ._anvil_designer import Form1Template


def c(cell):
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
    {"title": "FOO", "width": 40},
]

tabledata = [
    {
        "id": 1,
        "name": "Oli Bob",
        "age": "12",
        "col": "red",
        "dob": date(1982, 5, 14),
    },
    {
        "id": 2,
        "name": "Mary May",
        "age": "1",
        "col": "blue",
        "dob": date(1982, 5, 14),
    },
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

from random import randint

from ..Tabulator5 import Tabulator5

Tabulator5.theme = "modern"


class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.tabulator.data = tabledata
        self.tabulator.columns = columns
        self.tabulator.column_defaults = {"resizable": False}
        self.tabulator.options.update(
            selectable="highlight", pagination_size_selector=[1, 2, 5, 10]
        )

        # Any code you write here will run when the form opens.

    def tabulator_row_click(self, **event_args):
        print("click", event_args)

    def tabulator_cell_click(self, **event_args):
        print("cell click", event_args)

    def form_refreshing_data_bindings(self, **event_args):
        """This method is called when refreshing_data_bindings is called"""
        pass

    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        from time import sleep

        sleep(2)
        print(self.tabulator.columns)

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.tabulator.get_filters():
            self.tabulator.clear_filter()
        else:
            self.tabulator.set_filter(lambda data: data["col"] == "blue")


#         r = self.tabulator.add_data({
#             "id": randint(10, 10000000),
#             "name": "Me My",
#             "age": "190",
#             "col": "blue",
#             "dob": date(1988, 8, 1),
#         }, True)
#         print(r)
