# Anvil Tabulator
A dependency for anvil.works that wraps the JS Tabulator API

This app is available as a [third party dependency](https://anvil.works/forum/t/third-party-dependencies/8712) using the code: `TGQCF3WT6FVL2EM2`

|||
|---|---|
| Dependency Clone Link | [<img src="https://anvil.works/img/forum/copy-app.png" height='40px'>](https://anvil.works/build#clone:TGQCF3WT6FVL2EM2=SMZUM3MICK67JEIH25IJXCWP) |
|Live Example | [example-tabulator.anvil.app](https://example-tabulator.anvil.app/) |
|Example Clone Link | [<img src="https://anvil.works/img/forum/copy-app.png" height='40px'>](https://anvil.works/build#clone:JVL5ORAAPZ6SVWDU=JA27THWRHTGHH7XK4U36PRN4)|

---

## Differences between JS Tabulator and Anvil Tabulator

In JS Tabulator a tabulator instance is defined like:
```js
var table = new Tabulator("#example-table", {
 	data:tabledata,
 	layout:"fitColumns",
 	columns:[
	 	{title:"Name", field:"name", width:150},
	 	{title:"Age", field:"age", hozAlign:"left", formatter:"progress"},
	 	{title:"Favourite Color", field:"col"},
	 	{title:"Date Of Birth", field:"dob", sorter:"date", hozAlign:"center"},
 	],
     // other options within this object
});
```
In Anvil Tabulator add the Tabulator Component in the design view and then set the data and columns at runtime.

```python
    self.tabulator.data = table_data
    self.tabulator.columns = [
        {"title":"Name", "field":"name", "width":150},
	 	{"title":"Age", "field":"age", "hoz_align":"left", "formatter":"progress"},
	 	{"title":"Favourite Color", "field":"col"},
	 	{"title":"Date Of Birth", "field":"dob", "sorter":"date", "hoz_align":"center"},
    ]

```

### Defining options

In JS Tabulator options are defined within the object parsed to Tabulator constructor.

In Anvil Tabulator, some options are available in the designer as properties.
Other options can be set at runtime.

Either by setting overriding the `options` property
```python
self.tabulator.options = {
    "selectable": "highlight",
    "pagination_size_selector": [1, 2, 5, 10]
}
```

or by updating it
```python
self.tabulator.options.update(
    selectable="highlight",
    pagination_size_selector=True,
)

self.tabulator.options["langs"] = {
    "fr": {
        "columns": {
            "name":"Nom",
            "progress":"Progression",
            "gender":"Genre",
            "rating":"Évaluation",
            "col":"Couleur",
            "dob":"Date de Naissance",
        },
    }
}
```

### Events

Some JS Tabulator events are available in the design view.

```python

def tabulator_row_click(self, row, **event_args):
    alert(f"row with id {row.get_index()} was clicked")

```

Other JS Tabulator events can be added using the `on()` method

```python
    self.tabulator.on("header_click", self.header_click)


def header_click(self, e, column):
    alert(f"{column.get_field()!r} column was clicked")
```

### Methods

Some JS Tabulator methods are available in the Anvil autocompleter.
Any method in the autocompleter is just there for convenience.
Calling a JS Tabulator method directly calls the JS method.

Any methods not available in the autocompleter can also be called.
Check the call signatures in the JS Tabulator docs.

Keyword arguments are not supported (JS doesn't do keyword arguments).

```python
# not available in the autocomplete but can still be called
self.tabulator.previous_page()
```

### Table Built

Calling tabulator methods is only possible once the tabulator instance has been built.
This happens after the form show event, and a handler can be set on the `table_built` event.

Doing something like this in the `__init__` method

```python
self.tabulator.set_sort("name", "asc")
```
would throw an `AttributeError` since the tabulator instance does not exist yet.

Instead do:
```python
def tabulator_table_built(self, **event_args):
    self.tabulator.set_sort("name", "asc")

```

The exception to this is the `self.tabulator.on()` and `self.tabulator.off()` method.
These can be called before the tabulator is built.


### Snake Case

JS tabulator uses camelCase. Whereas Python formatting guide suggests snake case.
You can use camelCase but if you prefer to use snake case it is supported in the following places.

- any tabulator instance method
- any method called on a tabulator row, cell or column
- any event name called using the `on` method
- keys in the tabulator `options` definition
- keys in the tabulator `column` definition
- keys in the tabulator `column_defaults` definition

Snake case is not supported for any values in the definition.

e.g.

```python
self.tabulator.columns = [
    ...
    {"title":"Email", "field":"email", "formatter":"link", "formatter_params":{
        "labelField":"name",
        "urlPrefix":"mailto://", # must be camelCase
        "target":"_blank",
    }}
]

```

`labelField` and `urlPrefix` are part of the `formatter_params` value so must be camelCase.


### Formatters, Sorters, Editors, Filters

JS Tabulator supports custom Formatters, custom Sorters, custom Editors and custom Filters.
In these cases, when using a function as a Formatter, Sorter, Editor or Filter,
the call signature differs from the one described in the JS Tabulator docs.

**Custom Formatter**

Can be either a function, Anvil Component or Anvil Form.
If it is a function it should return an Anvil Component, dom node or string or dom string.

in JS Tabulator
```js
function nameFormatter(cell, formatterParams, onRendered) {
    return "Mr" + cell.getValue();
}

[
    {title:"Name", field:"name", formatter: nameFormatter},
    ...
]

```

in Anvil Tabulator
```python
def name_formatter(cell, **params):
    return "Mr" + cell.get_value()

self.tabulator.columns = [
    {"title":"Name", "field":"name", "formatter": name_formatter},
    ...
]
```

If `formatter_params` are used, these will be passed as keyword arguments to the function.
`formatter_params` can also be a function that returns a dictionary e.g.

```python
def get_image_params(cell):
    return dict(source=cell.get_value(), height=50, spacing_above="none", spacing_below="none")

self.tabulator.columns = [
    ...
    {'title': 'Image', 'field':'image', 'formatter': Image, 'formatter_params': get_image_params},
]
```

If using a Form as the `formatter` then the `data` for the current row will be passed as the `item` allowing data bindings to be used.


**Custom Editors**

I'd probably recommend avoiding custom editors, instead favouring an Anvil alert to make edits and then updating the tabulator row.

Or only use the built-in formatters and catch changes using the `cell_edited` event.

JS Tabulator uses the browser blur event to determine when to close the editor,
but the blur events aren't exposed in Anvil which is problematic.

There is an example of a custom editor in the Example source code above.
You can use `anvil_extras.augment` to add blur events.

e.g.

```python
from anvil_extras import augment

class ColorEditor(ColorEditorTemplate):
    def __init__(self):
        self.textbox.text = self.item["color"]
        augment.add_event_handler(self.textbox, "blur", self.textbox_blur)

    def textbox_presssed_enter(self, **event_args):
        self.raise_event('x-close-editor', value=self.textbox.text)

    def textbox_blur(self, **event_args):
        self.raise_event('x-close-editor', value=self.textbox.text)
```

```python

from .ColorEditor import ColorEditor

    self.tabulator.columns = [
  	 	{"title":"Favourite Color", "field":"color", "editor": ColorEditor},
    ]

```

Just like with custom Formatters, if the custom Editor is an Anvil Form,
then the item property will be the data for that row.

Similarly, a function can be used that returns a Component e.g.

```python

def color_editor(cell, **editor_params):
    tb = TextBox(text=cell.get_value(), spacing_above="none", spacing_below="none")
    def blur(**event_args):
        tb.raise_event("x-close-editor", value=tb.text)
            self.textbox.text = self.item["color"]
    augment.add_event(tb, "blur")
    tb.add_event_handler("blur", blur)
    tb.add_event_handler("pressed_enter", blur)
    return tb

```

**Custom Sorters**

In JS Tabulator

```js
    {title:"Name", field:"name", sorter:function(a, b, aRow, bRow, column, dir, sorterParams){
        return a - b; //you must return the difference between the two values
    }}
```

in Anvil Tabulator

```python
def name_sorter(a, b, **params):
    return a - b

self.tabulator.columns = [
    {"title":"Name", "field":"name", "sorter":name_sorter}
]

```

**Custom Filters**

In JS Tabulator

```js
function customFilter(data, filterParams){
    //data - the data for the row being filtered
    //filterParams - params object passed to the filter

    return data.name == "bob" && data.height < filterParams.height; //must return a boolean, true if it passes the filter.
}

table.setFilter(customFilter, {height:3});
```

in Anvil Tabulator

```python

def custom_filter(data, **params):
    return data["name"] == "bob" and data["height"] < params["height"]

self.tabulator.set_filter(custom_filter, {"height":3})

```
### Dates and Datetimes

JS Tabulator favours strings as dates and datetimes whereas
Anvil favours python date and datetime objects.

This is reflected in the built-in `"date"` and `"datetime"` Formatters, Editors and Sorters.
These built-in Formatters, Editors and Sorters have been overridden to expect python objects.

```python
    self.tabulator.columns = [
        ...
        {
            "title": "Date Of Birth",
            "field": "dob",
            "editor": "date",
            "sorter": "date",
            "formatter": "date",
            "formatter_params": {"format": "%d/%m/%Y"},
        },
    ]

```

In JS Tabulator the `formatter_params` expects an `"inputFormat"` and an `"outputFormat"`.
In Anvil Tabulator `formatter_params` expects a `"format"` which can also be `"iso"`.
The `"format"` param should match python formatting for `strftime()`.
A `tz` or `timezone` param is also supported for `datetimes`.

```python
    self.tabulator.columns = [
        ...
        {
            "title": "Last Login",
            "field": "last_login",
            "sorter": "datetime",
            "formatter": "datetime",
            "formatter_params": {"format": "iso", "tz": None},
        },
    ]
```

If `"tz"` is set to `None` it will use the browser timezone.
Otherwise, it can be set to an Anvil.tz object e.g.

```python
            "formatter_params": {"tz": anvil.tz.tz_local()},

```


### Modules

JS Tabulator has a modular design.
To add features a Module that exposes those features can be added

```js

import {Tabulator, FormatModule, EditModule} from 'tabulator-tables';

Tabulator.registerModule([FormatModule, EditModule]);

var table = new Tabulator("#example-table", {
  //table setup options
});

```

In Anvil Tabulator certain modules are included by default.

```python
from tabulator.Tabulator import Tabulator
Tabulator.modules = {
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
```
i.e. the modules property on the Tabulator component is a set of strings.
These modules will be registered at runtime before the first Tabulator instance is created.
You can adjust this list by adjusting the set.

```python

Tabulator.modules.remove("FrozenColumns")
Tabulator.modules.add("Persistance")

```

or by overriding the modules property with a new `set`, `list`, `tuple` of modules.


### Themes

Anvil Tabulator uses JS Tabulator's `"bootstrap3"` theme.

Some other pre-written themes can be used with Anvil Tabulator.

**Changing the theme**

```python
from tabulator.Tabulator import Tabulator

Tabulator.theme = "midnight" # "standard", "simple", "modern"

# or a custom theme

Tabulator.theme = "/_/theme/my_theme.css"

# or handle theming yourself in native libraries

Tabulator.theme = None

```

To add bootstrap3 alternative table stripes you can add the `table-striped` CSS class
using the `css_class` option.

```python
self.tabulator.options.update(css_class="table_striped")
```

other common CSS classes for the bootstrap theme can be added like

```python
self.tabulator.options.update(css_class=["table_striped", "table_bordered", "table_condensed"])
```

### Default Options

JS Tabulator has various default options.

In JS Tabulator:
```python
Tabulator.defaultOptions.layout = "fitData"
```

In Anvil Tabulator
```python
from tabulator.Tabulator import Tabulator
Tabulator.default_options["layout"] = "fitData"
```
