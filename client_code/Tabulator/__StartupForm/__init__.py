from ._anvil_designer import __StartupFormTemplate
from anvil import *


class __StartupForm(__StartupFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.tabulator_1.data = [
            {
                "columnA": "columnA",
                "columnB": "columnB",
                "columnC": "columnC",
                "columnD": "columnD",
            },
            {
                "columnA": "columnA",
                "columnB": "columnB",
                "columnC": "columnC",
                "columnD": "columnD",
            },
        ]
