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
      col['editor'] = self._clean_formatter(formatter)

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
  
  if isinstance(formatter, Component):
    is_template = formatter.__base__.__name__.endswith('Template')
    # then are we a Template?
    
    def loadComponentCell(cell, formatterParams, onRendered):
      formatterParams = formatterParams or {}
      if is_template:
        item = cell.getData()
        component = formatter(item={**item}, **formatterParams)
      else:
        component = formatter(**formatterParams)
      self.add_component(component) # make sure we have a parent
      return get_dom_node(component)
    return loadComponentCell

  elif callable(formatter):
    
    def loadFunctionCell(cell, formatterParams, onRendered):
      formatterParams = formatterParams or {}
      print(cell.getData())
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
   
def _clean_editor(self, formatter, params):
  if isintance(formatter, str):
    return formatter
    
    

      
"""
function set_columns(self, columns, checkbox_select) {
	const Component =  PyDefUtils.getModule('anvil').$d.Component;
    const load_component = function (formatter, cell, parameters) {
        // get the row as a python dict
        let row;
        // get a kwargs array from the paramaters
        let kwargs = [];
        Sk.abstr.mappingUnpackIntoKeywordArray(kwargs, PyDefUtils.unwrapOrRemapToPy(parameters));
        const base = Sk.abstr.lookupSpecial(formatter, new Sk.builtin.str("__base__"));
        debugger
      	const baseName = base && Sk.abstr.lookupSpecial(base, Sk.builtin.str.$name);
        if (baseName && baseName.toString().includes('Template')) {
          const item = ["item", PyDefUtils.unwrapOrRemapToPy(cell.getData())]
          kwargs = kwargs.concat(item);
        } else if (formatter instanceof Sk.builtin.method) {
          row = [PyDefUtils.unwrapOrRemapToPy(cell.getData())];
        } else if (formatter instanceof Sk.builtin.func) {
          row = [PyDefUtils.unwrapOrRemapToPy(cell.getData())];
        }
        let component = Sk.misceval.callsimArray(formatter, row, kwargs);
        if (!Sk.builtin.checkString(component)) {
          anvil.call(table.element, 'add_component', component);
        }
      return component;
    }
    
    for (let i = 0; i < columns.length; i++) {
        const c = columns[i]
        if (typeof c.formatter == 'object' && c.formatter.v !== undefined) {
          	// then we have an anvil element
          	const formatter_component = c.formatter.v;
          	c.formatter = function (cell, formatterParams, onRendered) {
            let formatter = load_component(formatter_component, cell, formatterParams);
            if (Sk.builtin.checkString(formatter)) {
              return formatter.$jsstr();
            }
            return formatter._anvil.element[0];
            }
        }

        if (typeof c.editor == 'object' && c.editor.v !== undefined) {
            // then we have an anvil element
            const editor_component = c.editor.v;
            c.editor = function (cell, onRendered, success, cancel, editorParams) {
                let component = load_component(editor_component, cell, editorParams);
              	let editor = component._anvil.element;
                const blur_cancel = function (e) {
                    if (!e.target.parentElement.classList.contains('anvil-datepicker') || (e.relatedTarget && e.relatedTarget.tagName !== 'SELECT')) {
                        // hack for datepicker
                        cancel()
                    }
                }
                editor[0].addEventListener('blur', blur_cancel, true);
                
                const close_editor = function (kwa) {
                    cancel()
                    if (component._anvil.parent) {
                        Sk.abstr.gattr(component, Sk.builtin.str('remove_from_parent')).tp$call([])
                    }
                };
                close_editor.co_kwargs = 1;
                component._anvil.eventHandlers['x-close-editor'] = new Sk.builtin.func(close_editor);
                
              	editor.css('padding', '8px');

                onRendered(function () {
                    // focus the first non-div element
                    editor.find(':not(div)').first().trigger('focus');
                });
                return editor[0];
            }
        }
      if (typeof c.sorter === 'object' && Sk.builtin.checkFunction(c.sorter.v)) {
        const pySorter = c.sorter.v;
        const sorterParams = [];
        Sk.abstr.mappingUnpackIntoKeywordArray(sorterParams, PyDefUtils.unwrapOrRemapToPy(c.sorterParams || {}));
        c.sorter = function (a, b, aRow, bRow, column, dir) {
          a = PyDefUtils.unwrapOrRemapToPy(a);
          b = PyDefUtils.unwrapOrRemapToPy(b);
          aRow = PyDefUtils.unwrapOrRemapToPy(aRow.getData());
          bRow = PyDefUtils.unwrapOrRemapToPy(bRow.getData());
          const val = Sk.misceval.callsimArray(pySorter, [a, b, aRow, bRow,], sorterParams);
          return Sk.ffi.remapToJs(val);
        }
      }
    }
    table.setColumns(columns);
}
"""

def _clean_sorter(self, sorter):
  if isinstance(sorter, str):
    return sorter
  if callable(sorter):
    def sorterWrapper(a, b, aRow, bRow, column, asc_or_dec, sorterParams): 
      return sorter(a, b, aRow, bRow, **sorterParams)

  
  
  
  
  
  
  