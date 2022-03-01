from anvil.js.window import RegExp, String

_RE_SNAKE = RegExp("_[a-z]", "g")
_replace = String.prototype.replace

def snake_to_camel(s):
    return _replace.call(s, _RE_SNAKE, lambda m, *_: m[1].upper())
