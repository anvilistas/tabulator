from anvil.js.window import RegExp, String

_RE_SNAKE = RegExp("_[a-z]", "g")
_replace = String.prototype.replace

def _toCamel(s):
    return _replace.call(s, _RE_SNAKE, lambda m, *_: m[1].upper())


def _merge_from_default(default, properties):
    merged = {}
    for key, val in default.items():
        merged = properties.get(key, val)
    return merged
