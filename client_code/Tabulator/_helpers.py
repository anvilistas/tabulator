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
    msg = e.get("message", "")
    if "ResizeObserver loop" in msg or "Script error." == msg:
        e.stopPropagation()
        e.stopImmediatePropagation()


def _ignore_resize_observer_error():
    # we need this error handler to fire first so we can stopImmediatePropagation
    onerror = window.onerror
    window.onerror = None
    window.addEventListener("error", _ignore_resize_observer_error_handler)
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
        theme = f"https://cdn.jsdelivr.net/npm/tabulator-tables@5.1.3/dist/css/tabulator{theme}.min.css"
    link.href = theme
    link.rel = "stylesheet"
#     link.integrity="sha256-X+nZ8IG0y1s7r4idlK2src96HsOSClbD7VZTMPpXo9s="
    link.crossorigin="anonymous"

    def do_wait(res, rej):
        link.onload = res
        link.onerror = rej

    document.body.appendChild(link)
    p = Promise(do_wait)
    anvil.js.await_promise(p)


def _to_module(modname):
    if not isinstance(modname, str):
        return modname
    if not modname.endswith("Module"):
        modname += "Module"
    return TabulatorModule[modname]


# from anvil-extras
def _spacing_property(a_b):
    def getter(self):
        return getattr(self, "_spacing_" + a_b, "")

    def setter(self, value):
        self._dom_node.classList.remove(
            f"anvil-spacing-{a_b}-{getattr(self, '_spacing_' + a_b, '')}"
        )
        self._dom_node.classList.add(f"anvil-spacing-{a_b}-{value}")
        setattr(self, "_spacing_" + a_b, value)

    return property(getter, setter, None, a_b)
