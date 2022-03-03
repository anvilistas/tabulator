# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

import anvil.js
from anvil.js.window import Promise, RegExp, String, document, window

from ._js_tabulator import TabulatorModule

_RE_SNAKE = RegExp("_[a-z]", "g")
_replace = String.prototype.replace


def _toCamel(s):
    return _replace.call(s, _RE_SNAKE, lambda m, *_: m[1].upper())


def _camelKeys(d):
    return {_toCamel(key): val for key, val in d.items()}


def _merge(default, properties, **overrides):
    merged = overrides
    for key, val in default.items():
        merged[key] = properties.get(key, val)
    return merged


# ignore harmless errors that will cause Anvil popups
# see example issue https://github.com/souporserious/react-measure/issues/104
def _ignore_resize_observer_error_handler(e):
    # This covers both
    # - 'ResizeObserver loop limit exceeded', and
    # - 'ResizeObserver loop ocmpleted with undelivered notifications'
    if "ResizeObserver loop" in e.get("message", ""):
        e.stopPropagation()
        e.stopImmediatePropagation()


def _ignore_resize_observer_error():
    # we need this error handler to fire first so we can stopImmediatePropagation
    onerror = window.onerror
    window.onerror = None
    window.addEventListener("error", _ignore_resize_observer_error)
    window.onerror = onerror


_warnings = {}


def _options_property(key, getMethod=None, setMethod=None):
    def option_getter(self):
        if getMethod is None or self._t is None:
            return self._options.get(key)
        else:
            return self._t[getMethod]()

    def option_setter(self, value):
        self._options[key] = value
        if self._t is None:
            return
        elif setMethod is not None:
            return self._t[setMethod](value)
        elif _warnings.get("post_init") is not None:
            return
        _warnings["post_init"] = True
        print(
            f"Warning: chaning the option {key!r} after the table has been built has no effect"
        )

    return property(option_getter, option_setter)


_themes = {
    "standard",
    "simple",
    "midnight",
    "modern",
    "bootstrap3",
}


def _inject_theme(theme):
    style = document.createElement("style")
    style.textContent = """
    .tabulator-cell .column-panel, .tabulator-cell input {margin: 0 !important;}
    .tabulator-cell .form-control {padding-top: 0 !important;}
    """
    document.body.appendChild(style)
    if not theme:
        return
    link = document.createElement("link")
    if theme in _themes:
        theme = "_" + theme if theme != "standard" else ""
        theme = f"https://cdn.skypack.dev/tabulator-tables@5.1.2/dist/css/tabulator{theme}.min.css"
    link.href = theme
    link.rel = "stylesheet"

    def do_wait(res, rej):
        link.onload = res
        link.onerror = lambda e: rej(Exception(f"{theme} was not loaded"))

    document.body.appendChild(link)
    p = Promise(do_wait)
    anvil.js.await_promise(p)


def _to_module(modname):
    if not isinstance(modname, str):
        return modname
    if not modname.endswith("Module"):
        modname += "Module"
    return TabulatorModule[modname]
