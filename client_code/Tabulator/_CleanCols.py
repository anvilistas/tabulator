from anvil.js import get_dom_node
from anvil import Component

def _clean_cols(self, cols):
    add_check_box_col = self._row_selectable=='checkbox'
    cols = cols or []

    for col in cols:
        formatter = col.get('formatter')
        if formatter is not None:
            col['formatter'] = self._clean_formatter(formatter)
    
        editor = col.get('editor')
        if editor is not None:
            col['editor'] = self._clean_editor(editor)

        sorter = col.get('sorter')
        if sorter is not None:
            col['sorter'] = self._clean_sorter(sorter)
    
    if add_check_box_col:
        cols = [{
                'formatter': "rowSelectionDisplay",
                'titleFormatter': "rowSelectionDisplay",
                'width': 40,
                'align': "center",
                'headerSort': False,
                'cssClass': 'title-center',
                'cellClick': lambda e, cell: cell.getRow().toggleSelect()
            }] + cols
    
    return cols


def _clean_formatter(self, formatter):
    if isinstance(formatter, str):
        return formatter
    
    
    if isinstance(formatter, type) and issubclass(formatter, Component):
        is_template = formatter.__base__.__name__.endswith('Template')
        # then are we a Template?

        def loadComponentCell(cell, formatterParams, onRendered):
            formatterParams = formatterParams or {}
            if is_template:
                component = formatter(item={**cell.getData()}, **formatterParams)
            else:
                component = formatter(**formatterParams)
            self.add_component(component) # make sure we have a parent
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
    def blur_cancel(e):
        # hack for datepicker
        if (not e.target.parentElement.classList.contains('anvil-datepicker') or (e.relatedTarged and e.relatedTarget.tagName != 'SELECT')):
            cancel()

    el = get_dom_node(component)
    el.addEventListener('blur', blur_cancel, True)
    el.style.padding = '8px'
    def close_editor(**event_args):
        cancel()
        component.remove_from_parent()

    component.set_event_handler('x-close-editor', close_editor)
    
    def set_focus(*args):
        to_focus = el.querySelector(':not(div)')
        print(to_focus)
        to_focus = to_focus or el
        to_focus.focus()
    onRendered(set_focus)
    return el
  

def _clean_editor(self, editor):
    print('here', editor)
    if isinstance(editor, str):
        return editor
    
    elif isinstance(editor, type) and issubclass(editor, Component):
        is_template = editor.__base__.__name__.endswith('Template')
        print('component subclass', is_template)
        # then are we a Template?
        def loadEditor(cell, onRendered, success, cancel, editorParams):
            print('editor loading')
            if is_template:
                component = editor(item={**cell.getData()}, **editorParams)
            else:
                component = editor(**editorParams)
            
            el = setup_editor_component(component, cancel, onRendered)

            
            return el

        return loadEditor

    elif callable(editor):
        def loadFunctionEditor(cell, onRendered, success, cancel, editorParams):
            maybe_component = editor(dict(cell.getData()), **editorParams)
            if isinstance(maybe_component, Component):
                el = setup_editor_component(maybe_component, cancel, onRendered)
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
            return sorter(a, b, dict(aRow), dict(bRow), asc == "asc", **sorterParams)
    else:
        return sorter
  
  
  
  
#       const load_component = function (formatter, cell, parameters) {
#         // get the row as a python dict
#         let row;
#         // get a kwargs array from the paramaters
#         let kwargs = [];
#         Sk.abstr.mappingUnpackIntoKeywordArray(kwargs, PyDefUtils.unwrapOrRemapToPy(parameters));
#         const base = Sk.abstr.lookupSpecial(formatter, new Sk.builtin.str("__base__"));
#         debugger
#       	const baseName = base && Sk.abstr.lookupSpecial(base, Sk.builtin.str.$name);
#         if (baseName && baseName.toString().includes('Template')) {
#           const item = ["item", PyDefUtils.unwrapOrRemapToPy(cell.getData())]
#           kwargs = kwargs.concat(item);
#         } else if (formatter instanceof Sk.builtin.method) {
#           row = [PyDefUtils.unwrapOrRemapToPy(cell.getData())];
#         } else if (formatter instanceof Sk.builtin.func) {
#           row = [PyDefUtils.unwrapOrRemapToPy(cell.getData())];
#         }
#         let component = Sk.misceval.callsimArray(formatter, row, kwargs);
#         if (!Sk.builtin.checkString(component)) {
#           anvil.call(table.element, 'add_component', component);
#         }
#       return component;
#     }
    
  
  