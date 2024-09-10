# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from functools import partial, wraps

import anvil.js
from anvil.js.window import Function, Promise, RegExp, String, document, window

try:
    from anvil.designer import in_designer
except ImportError:
    in_designer = False

from ._js_tabulator import TabulatorModule, theme_url

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
    # - 'ResizeObserver loop completed with undelivered notifications'
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
        if setMethod is not None:
            return self._t[setMethod](value)
        if in_designer:
            self._t.destroy()
            self._initialize()
            return
        if _warnings.get("post_init") is not None:
            return
        _warnings["post_init"] = True
        msg = f"Warning: changing the option {key!r} after the table has been built has no effect"
        print(msg)

    return property(option_getter, option_setter)


_themes = {
    "standard",
    "simple",
    "midnight",
    "modern",
    "bootstrap3",
    "bootstrap4",
    "materialize",
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
        theme = theme_url.format(theme)
    link.href = theme
    link.rel = "stylesheet"
    link.crossorigin = "anonymous"

    def do_wait(res, rej):
        link.onload = res
        link.onerror = lambda e: print(f"ERROR: Failed to load theme {theme}")

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


do_call = Function(
    "fn",
    "return Sk.misceval.callsimArray(Sk.ffi.toPy(fn));",
)


def assert_no_suspension(fn):
    @wraps(fn)
    def wrapped(*args, **kws):
        return do_call(partial(fn, *args, **kws))

    return wrapped
