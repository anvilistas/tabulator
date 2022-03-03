# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from anvil import *

from ._anvil_designer import Form2Template


class Form2(Form2Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
