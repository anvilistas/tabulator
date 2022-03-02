from .js_tabulator import Tabulator, TabulatorModule


_modules = ("Format", "Page", "Interaction", "Sort", "Edit", "Filter", "Menu", "SelectRow", "FrozenColumns", "FrozenRows")
_setup = False

def register_modules(*modules):
    global _setup
    if _setup:
        return
    _setup = True
    modules = modules or _modules
    for module in modules:
        module = getattr(TabulatorModule, module + "Module")
        Tabulator.registerModule(module)

    from . import callable_wrappers
    from . import datetime_overrides


Tabulator.defaultOptions.layout = "fitColumns";
Tabulator.defaultOptions.selectable = False;


from anvil.js import window

def _ignore_resize_observer_error(e):
    if "ResizeObserver loop" in e.get("message", ""):
        e.stopPropagation()
        e.stopImmediatePropagation()

# we need this error handler to fire first so we can stopImmediatePropagation
onerror = window.onerror 
window.onerror = None
window.addEventListener("error", _ignore_resize_observer_error)
window.onerror = onerror
