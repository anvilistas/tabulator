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


from anvil.js.window import Function

support_snake = Function("Component", """
const RE_SNAKE = new RegExp("_[a-z]", "g")
const to_camel = (s) => s.replace(RE_SNAKE, (m) => m[1].toUpperCase());

Object.setPrototypeOf(Component.prototype, new Proxy({}, {
    get(target, name, receiver) {
        const camel = to_camel(name);
        if (name === camel) return;
        return receiver[camel];
    }
}));
""")

for Component in "ColumnComponent", "CellComponent", "RowComponent":
    support_snake(TabulatorModule[Component])
