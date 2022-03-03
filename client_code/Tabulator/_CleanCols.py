from anvil import Component
from anvil.js import get_dom_node

"""
allow various types of formatters - Components, or wrapped functions

"""


def _clean_cols(self, cols):
    add_check_box_col = self._row_selectable == "checkbox"
    # make sure we do a shallow copy
    cols = [dict(col) for col in (cols or [])]

    for col in cols:
        formatter = col.get("formatter")
        if formatter is not None:
            formatter = self._clean_formatter(formatter)
        else:
            formatter = col.get("cellFormatter")
        if formatter is not None:
            col["formatter"] = formatter

        editor = col.get("editor")
        if editor is not None:
            col["editor"] = self._clean_editor(editor)

        sorter = col.get("sorter")
        if sorter is not None:
            col["sorter"] = self._clean_sorter(sorter)

    if add_check_box_col:
        cols = [
            {
                "formatter": "rowSelectionDisplay",
                "titleFormatter": "rowSelectionDisplay",
                "width": 40,
                "align": "center",
                "headerSort": False,
                "cssClass": "title-center",
                "cellClick": lambda e, cell: cell.getRow().toggleSelect(),
                "frozen": bool(cols) and cols[0].get("frozen", False)
            }
        ] + cols

    return cols


def _clean_formatter(self, formatter):
    if isinstance(formatter, str):
        return formatter

    if isinstance(formatter, type) and issubclass(formatter, Component):
        is_template = formatter.__base__.__name__.endswith("Template")
        # then are we a Template?

        def loadComponentCell(cell, formatterParams, onRendered):
            formatterParams = formatterParams or {}
            if is_template:
                component = formatter(
                    item={**cell.getData()}, **formatterParams
                )
            else:
                component = formatter(**formatterParams)
            self.add_component(component)  # make sure we have a parent
            return get_dom_node(component)

        return loadComponentCell

    elif callable(formatter):

        def loadFunctionCell(cell, formatterParams, onRendered):
            formatterParams = formatterParams or {}
            row = dict(cell.getData())
            cell_component_or_str = formatter(row, **formatterParams)
            if isinstance(cell_component_or_str, str):
                return cell_component_or_str
            elif isinstance(cell_component_or_str, Component):
                self.add_component(cell_component_or_str)
                return get_dom_node(cell_component_or_str)
            else:
                # oops hope for the best
                return cell_component_or_str

        return loadFunctionCell


def setup_editor_component(component, cancel, onRendered):
    closed = {}

    def blur_cancel(e):
        # hack for datepicker
        relatedTarget = getattr(e, "relatedTarget", None)
        if not e.target.parentElement.classList.contains(
            "anvil-datepicker"
        ) or (relatedTarget and relatedTarget.tagName != "SELECT"):
            if closed:
                return
            closed["x"] = True
            cancel()

    el = get_dom_node(component)
    el.addEventListener("blur", blur_cancel, True)
    el.style.padding = "8px"

    def close_editor(**event_args):
        if closed:
            return
        else:
            closed["x"] = True
        cancel()
        component.remove_from_parent()

    component.set_event_handler("x-close-editor", close_editor)

    def set_focus(*args):
        if component.visible is None:
            component.visible = True
        to_focus = el.querySelector(":not(div)")
        to_focus = to_focus or el
        to_focus.focus()

    onRendered(set_focus)
    return el


def _clean_editor(self, editor):
    if isinstance(editor, str):
        return editor

    elif isinstance(editor, type) and issubclass(editor, Component):
        is_template = editor.__base__.__name__.endswith("Template")
        # then are we a Template?
        def loadEditor(cell, onRendered, success, cancel, editorParams):
            if is_template:
                component = editor(item={**cell.getData()}, **editorParams)
            else:
                component = editor(**editorParams)

            el = setup_editor_component(component, cancel, onRendered)
            self.add_component(component)

            return el

        return loadEditor

    elif callable(editor):

        def loadFunctionEditor(cell, onRendered, success, cancel, editorParams):
            maybe_component = editor(dict(cell.getData()), **editorParams)
            if isinstance(maybe_component, Component):
                el = setup_editor_component(maybe_component, cancel, onRendered)
                self.add_component(maybe_component)
                return el
            else:
                return maybe_component

        return loadFunctionEditor

    else:
        return editor


def _clean_sorter(self, sorter):
    if isinstance(sorter, str):
        return sorter
    if callable(sorter):

        def sorterWrapper(a, b, aRow, bRow, column, asc, sorterParams):
            sorterParams = sorterParams or {}
            return sorter(
                a,
                b,
                aRow.getData(),
                bRow.getData(),
                asc == "asc",
                **sorterParams
            )

        return sorterWrapper
    else:
        return sorter
