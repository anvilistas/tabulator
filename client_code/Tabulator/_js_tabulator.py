# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

import anvil
from anvil.js import import_from, report_exceptions
from anvil.js.window import Function

# from anvil.js.window import TabulatorModule


config = anvil.app.get_client_config("tabulator")
cdn = config.get("cdn", True)
minified = config.get("minified", True)

if cdn:
    min = ",min" if minified else ""
    url = f"https://cdn.skypack.dev/pin/tabulator-tables@v6.2.5-B1KrV1TyUSjV9ySkbbZY/mode=imports{min}/optimized/tabulator-tables.js"
    theme_url = "https://cdn.jsdelivr.net/npm/tabulator-tables@6.2.5/dist/css/tabulator{}.min.css"
else:
    min = ".min" if minified else ""
    url = f"./_/theme/tabulator-tables/js/tabulator_esm{min}.js"
    theme_url = "./_/theme/tabulator-tables/css/tabulator{}.min.css"


TabulatorModule = import_from(url)


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
    "type",
    """
const RE_SNAKE = new RegExp("_[a-z]", "g")
const to_camel = (s) => s.replace(RE_SNAKE, (m) => m[1].toUpperCase());
const target = {sk$object: null, $isPyWrapped: false, $isSuspension: null};

Object.setPrototypeOf(Component.prototype, new Proxy(target, {
    get(target, name, receiver) {
        if (!(typeof name === "string")) return;
        const targetVal = target[name];
        if (typeof targetVal !== "undefined") return targetVal;
        const camel = to_camel(name);
        if (name === camel) return;
        const maybeRet = receiver[camel];
        if (typeof maybeRet !== "undefined") {
            return maybeRet;
        }
        const real = receiver["_" + type];
        return real.table.componentFunctionBinder.handle(type, real, camel);
    }
}));
""",
)

for component in "column", "cell", "row", "calc":
    support_snake(TabulatorModule[component.capitalize() + "Component"], component)


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


Function(
    "Module",
    """
const oldRegisterFunc = Module.prototype.registerTableFunction;

Module.prototype.registerTableFunction = function (name, func) {
    if (typeof this.table[name] !== "undefined") {
        console.warn("Unable to bind table function, name already in use", name);
    } else if (func.$isPyWrapped) {
        // don't wrap python functions with javascript functions - otherwise they won't support kwargs
        this.table[name] = func;
    } else {
        oldRegisterFunc.call(this, name, func)
    }
};

""",
)(TabulatorModule.Module)
