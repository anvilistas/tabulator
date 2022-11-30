# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

from datetime import date, datetime

from anvil import DatePicker
from anvil.js import get_dom_node, report_exceptions

from ._js_tabulator import FormatModule, SortModule, Tabulator

original_dt_formatter = FormatModule.formatters.datetime
original_dt_sorter = SortModule.sorters.datetime


def dt_formatter(dt_type, name, default_format):
    @report_exceptions
    def formatter(cell, params, onRendered):
        val = cell.getValue()
        if val is None:
            return None
        if not isinstance(val, dt_type):
            raise TypeError(
                f"A {name} formatter expects a {name} object, got {type(val).__name__}"
            )

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


def dt_sorter(compare):
    @report_exceptions
    def sorter(a, b, a_row, b_row, column, dir, params):
        align_empty_values = params.get("align_empty_values") or params.get(
            "alignEmptyValues"
        )
        if a == "":
            a = None
        if b == "":
            b = None

        empty_align = ""
        if a is None:
            empty_align = 0 if b is None else -1
        elif b is None:
            empty_align = 1
        else:
            return compare(a, b)
        if (
            align_empty_values == "top"
            and dir == "desc"
            or align_empty_values == "bottom"
            and dir == "asc"
        ):
            empty_align *= -1
        return empty_align

    return sorter


def dt_editor(pick_time):
    from ._custom_modules import EditorWrapper

    params = {
        "pick_time": pick_time,
        "spacing_above": "none",
        "spacing_below": "none",
        "font": "inherit",
    }

    if not pick_time:
        # because American formatting is horrible
        params["format"] = "DD/MM/YYYY"

    @report_exceptions
    def editor(cell, **properties):
        properties = params | properties
        value = cell.getValue()
        properties["date"] = value
        dp = DatePicker(**properties)
        dom_node = get_dom_node(dp)
        inputNode = dom_node.firstElementChild
        inputNode.style.fontSize = "inherit"
        inputNode.style.padding = "0"
        dom_node.style.display = "inline-flex"
        dom_node.style.justifyContent = "space-between"
        dom_node.style.height = "100%"
        dom_node.style.width = "100%"
        inputNode.nextSibling.style.bottom = "6px"

        def change(**event_args):
            dp.raise_event("x-close-editor", value=dp.date)

        dp.add_event_handler("change", change)

        def hide(**event_args):
            dp.date = dp.date  # force the calendar picker to close

        dp.add_event_handler("hide", hide)
        return dp

    return EditorWrapper.wrap(editor)


def init_overrides():
    Tabulator.extendModule(
        "format",
        "formatters",
        {
            "datetime": dt_formatter(datetime, "datetime", "%x"),
            "date": dt_formatter(date, "date", "%c"),
            "luxon_datetime": original_dt_formatter,
        },
    )
    Tabulator.extendModule(
        "sort",
        "sorters",
        {
            "datetime": dt_sorter(lambda a, b: a.timestamp() - b.timestamp()),
            "date": dt_sorter(lambda a, b: a.toordinal() - b.toordinal()),
            "luxon_datetime": original_dt_sorter,
        },
    )
    Tabulator.extendModule(
        "edit",
        "editors",
        {
            "datetime": dt_editor(True),
            "date": dt_editor(False),
        },
    )
