# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from anvil.js import import_from, report_exceptions
from anvil.js.window import Function

# from anvil.js.window import TabulatorModule
TabulatorModule = import_from(
    "https://cdn.skypack.dev/pin/tabulator-tables@v5.1.2-Od0AWBDAql7PzayHpzwZ/mode=imports,min/optimized/tabulator-tables.js"
)


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


support_snake = Function(
    "Component",
    """
const RE_SNAKE = new RegExp("_[a-z]", "g")
const to_camel = (s) => s.replace(RE_SNAKE, (m) => m[1].toUpperCase());
const target = {sk$object: null, $isPyWrapped: false, $isSuspension: false};

Object.setPrototypeOf(Component.prototype, new Proxy(target, {
    get(target, name, receiver) {
        if (!(typeof name === "string")) return;
        const targetVal = target[name];
        if (typeof targetVal !== "undefined") return targetVal;
        const camel = to_camel(name);
        if (name === camel) return;
        return receiver[camel];
    }
}));
""",
)

for Component in "ColumnComponent", "CellComponent", "RowComponent":
    support_snake(TabulatorModule[Component])


def filter_wrapper(f, params):
    params = params or {}

    @report_exceptions
    def wrapped(data):
        return f(data, **params)

    return wrapped


Function(
    "FilterModule",
    "wrapper",
    """
const findFilter = FilterModule.prototype.findFilter;

FilterModule.prototype.findFilter = function(filter) {
    if (typeof filter.field === 'function') {
        const wrapped = wrapper(filter.field, filter.type);
        Object.defineProperty(filter, "func", {get: () => wrapped, set: () => true });
    }
    return findFilter.call(this, filter);
}
""",
)(TabulatorModule.FilterModule, filter_wrapper)


Function(
    "FormatModule",
    """
const linkFormatter = FormatModule.formatters.link;
function linkWrapper(cell, params, onRendered) {
    const {url, urlPrefix, urlField} = params;
    if (!url && !urlPrefix && !urlField) {
        params.url = "javascript:void(0)";
    }
    return linkFormatter.call(this, cell, params, onRendered);
}
FormatModule.formatters.link = linkWrapper;
""",
)(TabulatorModule.FormatModule)
