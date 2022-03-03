from anvil.js.window import RegExp, String, window

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


def _ignore_resize_observer_error_handler(e):
    if "ResizeObserver loop" in e.get("message", ""):
        e.stopPropagation()
        e.stopImmediatePropagation()


def _ignore_resize_observer_error():
    # we need this error handler to fire first so we can stopImmediatePropagation
    onerror = window.onerror
    window.onerror = None
    window.addEventListener("error", _ignore_resize_observer_error)
    window.onerror = onerror
