# Anvil Tabulator
A dependency for anvil.works that wraps the JavaScript Tabulator Library (version 5.2)

This app is available as a [third party dependency](https://anvil.works/forum/t/third-party-dependencies/8712) using the code: `TGQCF3WT6FVL2EM2`

|||
|---|---|
| Dependency Clone Link | [<img src="https://anvil.works/img/forum/copy-app.png" height='40px'>](https://anvil.works/build#clone:TGQCF3WT6FVL2EM2=SMZUM3MICK67JEIH25IJXCWP) |
|Live Example | [example-tabulator.anvil.app](https://example-tabulator.anvil.app/) |
|Example Clone Link | [<img src="https://anvil.works/img/forum/copy-app.png" height='40px'>](https://anvil.works/build#clone:JVL5ORAAPZ6SVWDU=JA27THWRHTGHH7XK4U36PRN4)|

---

The documentation below should be read in conjunction with the [JS Tabulator docs (5.4)](http://tabulator.info/docs/5.4).


# Docs

- [Creating a Tabulator Component](#creating-a-tabulator-component)
- [Defining options](#defining-options)
- [Events](#events)
- [Methods](#methods)
- [Table Built](#table-built)
- [Snake Case](#snake-case)
- [Formatters, Sorters, Editors, Filters](#formatters-sorters-editors-filters)
- [Dates and Datetimes](#dates-and-datetimes)
- [Modules](#modules)
- [Themes](#themes)
- [Default Options](#default-options)
- [App Tables](#app-tables)
- [Using Models](#using-models)


---
### Creating a Tabulator Component

In JS Tabulator a tabulator instance is defined like:
```js
var table = new Tabulator("#example-table", {
 	data:tabledata,
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

---

### Defining options

In JS Tabulator options are defined within the object passed to Tabulator constructor.

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

---

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

---

### Methods

Some JS Tabulator methods are available in the Anvil autocompleter.
Any method in the autocompleter is just there for convenience.
Calling an Anvil Tabulator method directly calls the underlying JS method.

Any methods not available in the autocompleter can also be called.
Check the call signatures in the JS Tabulator docs.


```python
# not available in the autocomplete but can still be called
self.tabulator.previous_page()
```
Keyword arguments are not supported (JS doesn't have keyword arguments).

*(The only exception to this is `set_query()` which does support kwargs)*

---

### Table Built

Calling tabulator methods is only possible once the tabulator instance has been built.
This happens after the form show event, and a handler can be set on the `table_built` event.

Doing something like this in the `__init__` method

```python
self.tabulator.set_sort("name", "asc")
```
would throw an `AttributeError` or `RuntimeError` since the tabulator instance does not exist yet.

Instead do:
```python
def tabulator_table_built(self, **event_args):
    self.tabulator.set_sort("name", "asc")

```

The exception to this is the `self.tabulator.on()` and `self.tabulator.off()` method.
These can be called before the tabulator is built.


---

### Snake Case

JS tabulator uses camelCase. Whereas Python formatting guide suggests snake case.
You can always use camelCase but if you prefer to use snake case it is supported in the following places.

- any tabulator instance method
- any method called on a tabulator row, cell or column
- any event name called using the `on` method
- keys in the tabulator `options` definition
- keys in the tabulator `column` definition
- keys in the tabulator `column_defaults` definition

Snake case is not supported for any values in a definition.

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


---

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


**Row Selction Formatter**

If you need a checkbox style selection column you can add one manually.
Anvil Tabulator provides a default option

```python
from tabulator.Tabulator import row_selection_column

self.tabulator.columns = [
    row_selection_column,
    {'title': 'Image', 'field':'image', 'formatter': Image, 'formatter_params': get_image_params},
    ...
]

```

The definition for this column is:

```python
row_selection_column = {
    "formatter": "rowSelection",
    "title_formatter": "rowSelection",
    "title_formatter_params": {"rowRange": "visible"},
    "width": 40,
    "hoz_align": "center",
    "header_hoz_align": "center",
    "header_sort": False,
    "cell_click": lambda e, cell: cell.getRow().toggleSelect(),
}
```

If you use the `FrozenColumns` module you may need to add `"frozen": True` to this definiton.
Adding this column will turn on the `selectable` option to `"highlight"`. (Unless you've already set it in your options)



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

The `x-close-editor` event can be raised with or without a value.
When raised without a `value` paramater this is equivalent to  `self.raise_event("x-cancel")`.
When raised with a `value` parameter this is equivalent to raising the event `self.raise_event("x-success", value=value)`.

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

**Custom Header Filter**

A custom Header Filter component behaves much like an Custom Edit Component.
The only difference is that no `cell` argument is provided.


**Custom Header Filter Func**

If using Header Filters you may need a `header_filter_func` in your column definition.
This is particularly relevant with `datetime` objects where JS Tabulator doesn't know how to compare these objects.

```python
def header_filter_func(val, row_val, row_data, **params):
    return val in str(row_val)
```

---

### Dates and Datetimes

JS Tabulator favours strings as dates and datetimes whereas
Anvil favours python date and datetime objects.

This is reflected in the built-in `"date"` and `"datetime"` Formatters, Editors and Sorters.
These built-in Formatters, Editors and Sorters have been overridden to expect python objects.


_If you would like to use JS Tabulator datetime formatter/sorter use `"luxon_datetime"` in place of `"datetime"`._
_You will need `luxon.js` imported via CDN in your Native Libraries for this to work._


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
            "editor_params": {"format": "%d/%m/%Y"},
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



---

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


---

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
self.tabulator.options.update(css_class="table-striped")
```

other common CSS classes for the bootstrap theme can be added like

```python
self.tabulator.options.update(css_class=["table-striped", "table-bordered", "table-condensed"])
```

---

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

Note that `default_options` will not override any designer propeties.
e.g. setting `Tabulator.default_options["header_visible"] = False` will have no effect.


---

### App Tables

Anvil Tabulator provides an API for working with anvil `app_tables`
When working with `app_tables` your table should have a unique id column.
Set Tabulator's `index` property to the unique id column name.
Note Tabulator expects each data object to have an `index` key in order work with the data effectively.
If you don't have a unique id column then Tabulator will fallback to using the row id as the `index`.

To get started, instead of setting the `self.tabulator.data` attribute, provide the tabulator component with an `app_table` in the options.

```python
    self.tabulator.options = {
        "app_table": app_tables.my_table,
        "data_loader": False, # display JS Tabulators 'loading' component
        "loading_indicator": False # defaults to True - whether to use the anvil spinner during page loading
    }
```

*You may want to make a server call to retrieve a `client_readable` view of an `app_table`*

If an `app_table` option is provided the data will be retrieved by calling `.search()`.
The search will be adjusted depending on the header sorting.

Other options that work will with the `app_table` option:

```python
    self.tabulator.options = {
        "app_table": app_tables.my_table,
        "height" 400,
        "pagination": False,
        "progressive_load": "load", # enable progressive loading
        "progressive_load_delay": 200, # wait 200 milliseconds between each request
    }

    # OR

    self.tabulator.options = {
        "app_table": app_tables.my_table,
        "height" 400,
        "pagination": False,
        "progressive_load": "scroll", # load data into the table as the user scrolls
        "progressive_load_scroll_margin": 300, # trigger next data request when scroll bar is 300px or less from the bottom of the table
    }

```

It is also possible to set queries on the data, similar to JS Tabulator's `set_filter()` method.
Instead use `set_query()`. Any valid query using Anvil's query API will be supported.

```python
import anvil.tables.query as q

def text_box_1_change(self, **event_args):
    name = self.text_box_1.text
    if not name:
        self.tabulator.clear_query()
    else:
        self.tabulator.set_query(name=q.ilike(f"%{name}%"))

```

**Retrieving app_table rows**

If you want to retrieve an app_table row from the a tabulator event, use the `.get_table_row()` or `.get_table_rows()` method.

```python
def tabulator_row_click(self, row, **event_args):
    # row is a tabulator row_component
    # row.get_data() returns a javascript wrapped data object - probably not what you want
    data = row.get_data()
    # row.get_table_row() returns the original anvil app_table row 😃
    table_row = row.get_table_row()

def tabulator_cell_edited(self, cell, **event_args):
    cell = cell.get_table_row() # also possible

def select_visible(self):
    # returns a list of app_table rows that are visible
    self.tabulator.get_table_rows("visible")
```


All queries and searches are cached. If you need to reload/refresh the data in the tabulator component,
you can call `self.tabulator.replace_data()` or `self.tabulator.set_data()`.
This will create a fresh call to `search()` on the `app_table`, effectively clearing any cached values.
You can stay on the same page by surrounding the call with `x = self.tabulator.get_page()` and `self.tabulator.set_page(x)`.


**Row Selection Column with `app_table` option**

Using the `row_selection_column` does **not** work well with the `app_table` option.
If you want to use the `row_selection_column` with the `app_table` option it's best to
set the `progress_load` option to `"load"` and set `pagination` to `False`.



### Using Models

Anvil Tabulator provides an API for working with a list of models as opposed to a list of dicts.

Define the model that represents your data structure

```python
class Author:
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name

```

Add the following code, and set the `index` property in the designer to `uid` or in the `self.tabulator.options`.
(You must have a unique id property for each model instance)

```python
    self.tabulator.columns = [{"title":"Name", "field":"name"}]
    self.tabulator.options = {
        "index": "uid", # or set the index property here
        "use_model": True,
        "getter": getattr,
    }
    self.data = my_list_of_authors
```

By default the `getter` is set to `operator.getitem` i.e. it expects a dictionary.
For this model class, the data is generated by getting the name attribute on each Author instance,
and so changing the `getter` to the function `getattr()` is necessary.

All data sources must have a unique identifier. The field used as the unique identifier is set
by the `tabulator.index` property - this defaults to `"id"`. This can be changed in the design view or in the tabulator options.


If you want to retrieve the original models from tabulator events you can use the `get_model()` or `get_models()` methods.

```python
def tabulator_row_click(self, row, **event_args):
    # row is a tabulator row_component
    model = row.get_model()
    # the model associated with the tabulator row

def tabulator_cell_edited(self, cell, **event_args):
    model = cell.get_model()

def select_visible(self):
    self.tabulator.get_models("visible") # returns a list of models that are visible
```
