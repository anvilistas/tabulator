from anvil import Component
from anvil.js import get_component
from .js_tabulator import AbstractModule, register_module

@register_module("componentFormatter")
class ComponentFormatter(AbstractModule):
    def initialize(self):
        self.mod.subscribe("cell-format", self.cell_format)

    def cell_format(self, cell, prev):
        if isinstance(prev, Component):
            return get_dom_node(prev)
        return prev

@register_module("formatterWrapper", moduleInitOrder=1)
class FormatterWrapper(AbstractModule):
    def initialize(self):
        self.mod.subscribe("column-layout", self.wrap_formatters)

    def wrap_formatters(self, column):
        defintion = column.definition
        for suffix in "", "Print", "Clipboard", "HtmlOutput":
            option = "formatter" + suffix
            f = defintion.get(option)
            if f is None or not callable(f):
                continue
            defintion[option] = self.wrap(f)

    def wrap(self, f):
        if not isinstance(f, type) or not issubclass(f, Component):
            return lambda cell, params, onRendered: f(cell, **params)
        elif hasattr(f, "init_components"):
            return lambda cell, params, onRendered: f(item=dict(cell.getData()), **params)
        else:
            return lambda cell, params, onRendered: f(**params)
#
# lookupFormatter(column, type){
# 		var config = {params:column.definition["formatter" + type + "Params"] || {}},
# 		formatter = column.definition["formatter" + type];

# 		//set column formatter
# 		switch(typeof formatter){
# 			case "string":
# 			if(Format.formatters[formatter]){
# 				config.formatter = Format.formatters[formatter];
# 			}else{
# 				console.warn("Formatter Error - No such formatter found: ", formatter);
# 				config.formatter = Format.formatters.plaintext;
# 			}
# 			break;

# 			case "function":
# 			config.formatter = formatter;
# 			break;

# 			default:
# 			config.formatter = Format.formatters.plaintext;
# 			break;
# 		}

# 		return config;
# 	}
#     	initializeColumn(column){
# 		column.modules.format = this.lookupFormatter(column, "");

# 		if(typeof column.definition.formatterPrint !== "undefined"){
# 			column.modules.format.print = this.lookupFormatter(column, "Print");
# 		}

# 		if(typeof column.definition.formatterClipboard !== "undefined"){
# 			column.modules.format.clipboard = this.lookupFormatter(column, "Clipboard");
# 		}

# 		if(typeof column.definition.formatterHtmlOutput !== "undefined"){
# 			column.modules.format.htmlOutput = this.lookupFormatter(column, "HtmlOutput");
# 		}
# 	}
