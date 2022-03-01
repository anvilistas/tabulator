from .js_tabulator import Tabulator, TabulatorModule

for module in ["Format", "Page", "Interaction", "Sort", "Edit", "Menu", "MoveColumns", "MoveRows", "SelectRow"]:
    module = getattr(TabulatorModule, module + "Module")
    Tabulator.registerModule(module)

from . import callable_wrappers
from . import datetime_overrides

Tabulator.defaultOptions.layout = "fitColumns";
Tabulator.defaultOptions.selectable = False;
