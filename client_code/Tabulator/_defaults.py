# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

_event_call_signatures = {
    "row_click": ("event", "row"),
    "cell_click": ("event", "cell"),
    "row_tap": ("event", "row"),
    "cell_tap": ("event", "cell"),
    "cell_edited": ("cell",),
    "page_loaded": ("pageno",),
    "row_selected": ("row",),
    "row_deselected": ("row",),
    "row_selection_changed": ("data", "rows"),
    "table_built": (),
}

_default_options = {
    "auto_columns": False,
    "header_visible": True,
    "height": "",
    "index": "id",
    "pagination": True,
    "pagination_size": 5,
    "data": None,
    "columns": [],
    "column_defaults": {},
}

_default_props = {
    "spacing_above": "small",
    "spacing_below": "small",
    "border": "",
    "visible": True,
    "role": None,
}

_default_modules = {
    "Edit",
    "Filter",
    "Format",
    "FrozenColumns",
    "FrozenRows",
    "Interaction",
    "Menu",
    "Page",
    "ResizeColumns",
    "ResizeTable",
    "SelectRow",
    "Sort",
}

_default_table_options = {"layout": "fitColumns", "selectable": False}


_default_theme = "bootstrap3"

_methods = (
    "add_row",
    "delete_row",
    "update_row",
    "get_row",
    "select_row",
    "deselect_row",
    "get_selected_data",
    "add_data",
    "get_data",
    "update_or_add_data",
    "replace_data",
    "set_filter",
    "add_filter",
    "remove_filter",
    "get_filters",
    "clear_filter",
    "set_query",
    "clear_query",
    "clear_app_table_cache",
    "set_sort",
    "clear_sort",
    "get_page",
    "set_page",
)
