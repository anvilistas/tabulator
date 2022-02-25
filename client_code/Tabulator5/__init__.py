from ._anvil_designer import Tabulator5Template
from anvil import *

class Tabulator5(Tabulator5Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
