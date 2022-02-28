from anvil.js import import_from

TabulatorModule = import_from("https://cdn.skypack.dev/tabulator-tables@5.1.2")

def __getattr__(attr):
    global TabulatorModule
    return getattr(TabulatorModule, attr)


def __dir__():
    return [
        "AccessorModule",
        "AjaxModule",
        "CalcComponent",
        "CellComponent",
        "ClipboardModule",
        "ColumnCalcsModule",
        "ColumnComponent",
        "DataTreeModule",
        "DownloadModule",
        "EditModule",
        "ExportModule",
        "FilterModule",
        "FormatModule",
        "FrozenColumnsModule",
        "FrozenRowsModule",
        "GroupComponent",
        "GroupRowsModule",
        "HistoryModule",
        "HtmlTableImportModule",
        "ImportModule",
        "InteractionModule",
        "KeybindingsModule",
        "MenuModule",
        "Module",
        "MoveColumnsModule",
        "MoveRowsModule",
        "MutatorModule",
        "PageModule",
        "PersistenceModule",
        "PrintModule",
        "PseudoRow",
        "ReactiveDataModule",
        "Renderer",
        "ResizeColumnsModule",
        "ResizeRowsModule",
        "ResizeTableModule",
        "ResponsiveLayoutModule",
        "RowComponent",
        "SelectRowModule",
        "SortModule",
        "Tabulator",
        "TabulatorFull",
        "ValidateModule",
    ]


from anvil.js.window import RegExp, String, Object, Function
_replace = String.prototype.replace
_RE_CAMEL = RegExp("[a-z][A-Z]", "g")

def _camel_to_snake(s):
    return _replace.call(s, _RE_CAMEL, lambda m, *_: m[0] + "_" + m[1].lower())

CellComponent = TabulatorModule.CellComponent

support_snake = Function("ProxyComponent", """
const contr
""")


# for obj in ["Tabulator", "CellComponent", "RowComponent"]:

# 	constructor (cell){
# 		this._cell = cell;

# 		return new Proxy(this, {
# 			get: function(target, name, receiver) {
# 				if (typeof target[name] !== "undefined") {
# 					return target[name];
# 				}else{
# 					return target._cell.table.componentFunctionBinder.handle("cell", target._cell, name)
# 				}
# 			}
# 		})
# 	}