from anvil.js import import_from
from anvil.js.window import Function as _Function, document, Promise

from operator import attrgetter

def _import(*attrs):
    module = import_from(f"https://cdn.skypack.dev/tabulator-tables@5.1.2")
    print(dir(module))
    attrs = attrs or ["default"]
    return attrgetter(*attrs)(module)

Tabulator, Module, Accessor = _import("Tabulator", "Module", "AccessorModule")

transformRow = Accessor.prototype.transformRow

def tr(row, type, x):
    print("TRANSFORM ACCESSOR", row, type, x, sep="\n", end="\n\n")
    return row.data

Accessor.prototype.transformRow = tr

Accessor.prototype.initalize = lambda: print("OH WICKED")

print(Accessor.prototype.transformRow)


LoadModule = _Function("Module", "AnvilTabulator", "initializer", """
class AnvilModule extends Module {
    constructor(table) {
        super(table);
        AnvilTabulator(this, table);
    }
    initialize() {
        this._anvil.initalize();
    }
}
AnvilModule.moduleName = "anvil";
return AnvilModule;
""")


class AnvilTabulator:
    def __init__(self, mod, table):
        self.mod, self.table = mod, table
        mod._anvil = {"initalize": self.initialize}
        mod.registerTableOption("anvilFoo", True)
        self.data = []

    def initialize(self):
        print("being initialized")
        self.mod.subscribe("data-loading", self.data_loading)
        self.mod.subscribe("data-params", self.data_params)
        self.mod.subscribe("data-load", self.data_load)
        self.mod.subscribe("row-data-retrieve", self.transform_row)
    
    def data_loading(self, *args):
        print("data-loading", *args, sep="\n", end="\n\n")
        return True

    def data_params(self, *args):
        print("data-params", *args, sep="\n", end="\n\n")
        return {}

    def data_load(self, data, *args):
        print("data-load", *args, sep="\n", end="\n\n")
        self.data = data
        return Promise(lambda resolve, reject: resolve(data))
    
    def transform_row(self, row, type, prev):
        print("transforming row", row, type, prev, sep="\n", end="\n\n")
        return {**prev}


AnvilModule = LoadModule(Module, AnvilTabulator, AnvilTabulator.initialize)
Tabulator.registerModule(Accessor)
Tabulator.registerModule(AnvilModule)

Tabulator.extendModule("accessor", "accessors", {
    'roundDown': lambda value, *args: (print(value, "HEY"), value)[1][0]
})

el = document.createElement("div")

tabledata = [
 	{'id':1, 'name':"Oli Bob", 'age':"12", 'col':"red", 'dob':""},
 	{'id':2, 'name':"Mary May", 'age':"1", 'col':"blue", 'dob':"14/05/1982"},
 	{'id':3, 'name':"Christine Lobowski", 'age':"42", 'col':"green", 'dob':"22/05/1982"},
 	{'id':4, 'name':"Brendon Philips", 'age':"125", 'col':"orange", 'dob':"01/08/1980"},
 	{'id':5, 'name':"Margret Marmajuke", 'age':"16", 'col':"yellow", 'dob':"31/01/1999"},
]


table = Tabulator(el, {
    "anvilFoo": False,
    'data':tabledata,
   	'columns':[
	 	{'title':"Name", 'field':"name", 'width':150, 'accessor': 'roundDown'},
	 	{'title':"Age", 'field':"age", 'hozAlign':"left", 'formatter':"progress"},
	 	{'title':"Favourite Color", 'field':"col"},
	 	{'title':"Date Of Birth", 'field':"dob", 'sorter':"date", 'hozAlign':"center"},
 	],
})


table.on("dataProcessed", lambda data, *args: print("data", data is table.getData(), data, table.getData(), sep="\n", end="\n\n"))