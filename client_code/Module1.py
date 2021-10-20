from anvil.js import get_dom_node as _get_dom_node, import_from as _import_from

_TabulatorModule = _import_from("https://cdn.skypack.dev/tabulator-tables@5.0.2")
print(dir(_TabulatorModule))