from ._anvil_designer import Tabulator5Template
from anvil import *
from anvil.js.window import String, RegExp

_RE_SNAKE = RegExp("_[a-z]", "g")
_replace = String.prototype.replace

def _snake_to_camel(s):
    return _replace.call(s, _RE_SNAKE, lambda m, *_: m[1].upper())


class TabulatorQueuedCall:
    def __init__(self, attr, queue):
        self.attr = attr
        self.queue = queue

    def __call__(self, *args, **kws):
        self.queue.append([attr, args, kws])


class Tabulator5(Tabulator5Template):
    def __init__(self, **properties):
        self._options = {}
        self._el = None
        self._queued = []
        self._t = None
        self._init = False

    def _initialize(self):
        self._t = _Tabulator(self._el, self._options)
        for attr, args, kws in self._queued:
            getattr(self._t, attr)(*args, **kws)

    def __getattr__(self, attr):
        if self._t is None:
            return TabulatorQueuedCall(attr, self._queued)
        return getattr(self._t, attr)

    @staticmethod
    def _clean_key(item):
        return toCamelCase(item[0]), item[1]

    def _show(self, **event_args):
        if self._t is None:
            self._initialize()

    def define(self, **options):
        if self._init:
            raise RuntimeError("define must be called before the Tabulator component is on the screen")
        self._options |= map(lambda item: [_snake_to_camel(item[0]), item[1]], options.items())

    @property
    def data(self):
        if self._t is None:
            return self._options.get("data")
        return self._t.getData()

    @data.setter
    def data(self, value):
        # check the type of the value
        if self._t is None:
            self._options["data"] = value
        return self._t.setData(value)

    @property
    def columns(self):
        if self._t is None:
            return self._options.get("columns")

    @columns.setter
    def columns(self, value):
        if self._t is None:
            self._options["columns"] = value
        return self._t.getColumnDefinitions()
