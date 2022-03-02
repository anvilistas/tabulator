from .js_tabulator import Tabulator, TabulatorModule

for module in ["Format", "Page", "Interaction", "Sort", "Edit", "Filter", "Menu", "MoveColumns", "MoveRows", "SelectRow"]:
    module = getattr(TabulatorModule, module + "Module")
    Tabulator.registerModule(module)

from . import callable_wrappers
from . import datetime_overrides

Tabulator.defaultOptions.layout = "fitColumns";
Tabulator.defaultOptions.selectable = False;


from anvil.js import window

def ignore_resize_observer_error(e):
    if "ResizeObserver loop" in e.get("message", ""):
        e.stopPropagation()
        e.stopImmediatePropagation()

# we need this error handler to fire first so we can stopImmediatePropagation
onerror = window.onerror 
window.onerror = None
window.addEventListener("error", ignore_resize_observer_error)
window.onerror = onerror
