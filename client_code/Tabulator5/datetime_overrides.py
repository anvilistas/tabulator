from .js_tabulator import Tabulator
from datetime import date, datetime
from anvil import DatePicker

def dt_formatter(dt_type, name, default_format):
    def formatter(cell, params, onRendered):
        val = cell.getValue()
        if val is None:
            return ""
        if not isinstance(val, dt_type):
            raise TypeError(f"A {name} formatter expects a {name} object")

        if dt_type is datetime:
            tz = params.get("tz", False)
            if tz is False:
                tz = params.get("timezone", False)
            if tz is not False:
                val = val.astimezone(tz)

        out = params.get("format") or params.get("outputFormat", "%x")
        if out == "iso" or out == "isoformat":
            return val.isoformat()
        else:
            return val.strftime(out)
    return formatter


Tabulator.extendModule("format", "formatters", {
    "datetime": dt_formatter(datetime, "datetime", "%x"),
    "date": dt_formatter(date, "date", "%c"),
})


def dt_sorter(compare):
    def sorter(a, b, a_row, b_row, column, dir, params):
        align_empty_values = params.get("align_empty_values") or params.get("alignEmptyValues")
        empty_align = ""
        if a is None:
            empty_align = 0 if b is None else -1
        elif b is None:
            empty_align = 1
        else:
            return compare(a, b)
        if align_empty_values == "top" and dir == "desc" or align_empty_values == "bottom" and dir == "asc":
            empty_align *= -1
        return empty_align
    return sorter


Tabulator.extendModule("sort", "sorters", {
    "datetime": dt_sorter(lambda a, b: a.timestamp() - b.timestamp()),
    "date": dt_sorter(lambda a, b: a.toordinal() - b.toordinal()),
})


def dt_editor(pick_time):
    from .callable_wrappers import EditorWrapper
    params = {
        "pick_time": pick_time,
        "spacing_above": "none",
        "spacing_below": "none",
        "font": "inherit"
    }

    def editor(cell, **properties):
        properties = params | properties
        value = cell.getValue()
        properties["date"] = value
        dp = DatePicker(**properties)
        def change(**event_args):
            dp.raise_event('x-close-editor', value=dp.date)
        dp.add_event_handler("change", change)
        def hide(**event_args):
            dp.date = dp.date # force the calendar picker to close
        dp.add_event_handler("hide", hide)
        return dp

    return EditorWrapper.wrap(editor)

Tabulator.extendModule("edit", "editors", {
    "datetime": dt_editor(True),
    "date": dt_editor(False),
})
