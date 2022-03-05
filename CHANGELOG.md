# v2.0.0

## New Features

### `options`

Anvil only includes a handful of options to customize in the designer.
There are  many options available, JS Tabulator and it would be a nightmare to put them all in the designer.

If you find options in the JS Tabulator docs you can add them (as camel or snake case) using the options property

```python
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

This property can be overridden completely e.g.

```python
self.tabulator.options = {
    "selectable": "highlight",
    "pagination_size_selector": [1, 2, 5, 10]
}

```
But to have any effect it must be set before the form show event fires.

### `theme`

Tabulator ships with various themes, or you can write your own (see [JS Tabulator Docs](http://tabulator.info/docs/5.1/theme)).
The default theme is `"bootstrap3"` since Anvil ships with bootstrap 3.

You can change the theme:

```python
from tabulator.Tabulator import Tabulator

Tabulator.theme = "midnight" # "standard", "simple", "modern"

# or a custom theme

Tabulator.theme = "/_/theme/my_theme.css"

# or handle theming yourself in native libraries

Tabulator.theme = None


```

### `modules`

Tabulator 5.x has moved to a module design.
Features can be enhanced/redacted by changing the Tabulator modules.

See the full list of available Modules in the JS Tabulator docs.
http://tabulator.info/docs/5.1/modules#modules

Anvil Tabulator includes the following optional Modules
```python
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
You can adjust these by adding or removing, modules from the set of modules.
Or replace the set entirely.

```python
from tabulator.Tabulator import Tabulator

Tabulator.modules.remove("FrozenColumns")
Tabulator.modules.add("Persistance")
```

### `on`

Events not included by default can be accessed using `self.tabulator.on(event, handler)`.

Unlike other Tabulator methods, this can be called before the `table_built` event has fired.

There is also a `self.tabulator.off(event, handler=None)` method.

You can find events in the JS Tabulator docs.
Note that when using the `on` API the handler call signature should match the call signature from Javascript.

http://tabulator.info/docs/5.1/events


### `snake_case`

All table option keys can be defined as snake_case.
e.g.
```python
self.tabulator.options = {
    "paginationSizeSelector": [6, 10, 20]
}
# can be
self.tabulator.options = {
    "pagination_size_selector": [6, 10, 20]
}
```

All column defintion keys and column_default keys can be snake case
e.g.
```python
self.tabulator.columns = [
    {"title": "Name", "field": "name", "hoz_align": "right"},
    ...
]
self.tabulator.column_defaults = {
    "header_hoz_align": "center"
}
```

All tabulator events can be snake case

```python
self.tabulator.on("header_click", self.header_click)
```

All methods of the tabulator instance, cells, columns and rows can be called using snake case
```python
self.tabulator.previous_page() # or self.tabulator.previousPage()
```

```python
def header_click(self, event, column):
    alert(column.get_field()) # or column.getField()
```

Tabulator defines several pre-defined formatters.
The paramters keys must be camel case, e.g.

```python
# labelField, urlPrefix, must be camelCase
{"title":"Example", "field":"example", "formatter":"link", "formatter_params":{
    "labelField":"name",
    "urlPrefix":"mailto://", # must be camelCase
    "target":"_blank",
}}
```


### `default_options`

Tabulator has default options for various properties that can be overriden using `self.tabulator.options` attribute.

It's also possible to change these defaults without having to override them with the `options` attribute.

```python
from tabulator.Tabulator import Tabulator
Tabulator.default_options.update({"layout": "fitData", "selectable": True})
```

This is most useful if you have multiple Tabulator components and don't want to repeatedly set options.
The default `default_options` are:

```python
Tabulator.default_options = {"layout": "fitColumns", "selectable": False}
```
*(as well as all the JS Tabulator default options)*

### `column_defaults`

Check out the migration documentation for Tabulator 4.9 to 5.0: http://tabulator.info/docs/5.0/upgrade#column-defaults

column defaults can be set at runtime e.g.
```python
self.tabulator.column_defaults = {"resizable": False}
```

### `table_built` event

Use the `table_built` event to determine when you can start accessing methods on the tabulator instance.
Things like `self.tabulator.set_sort(...)` can only be called after the tabulator instance has been built.


## Breaking changes

We've moved from tabulator 4.6.x to tabulator 5.x
That means that some column definitions may not work as before.
If you've made heave use of the JS Tabulator API for column definitions you should check they still work.


### Package Name

The package name has changed from `Tabulator` to `tabulator`

```python
from Tabulator.Tabulator import Tabulator
# too many Tabulators

# becomes
from tabulator.Tabulator import Tabulator
```

### Calling Methods

It's no longer possible to call methods on a tabulator object until it's been built.
If you try to call a method too early you'll get an `AttributeError`.

There is a new `tabulator_built` event that you can use.
The `tabulator_built` event will be called after the `form_show` event.

### Custom Sorter

If you were previously defining a function as a sorter the call signature has changed:

```python
{"title": "Age", "field": "age", "sorter": lambda a, b, aRow, bRow, asc, **params: a - b}

# becomes

{"title": "Age", "field": "age", "sorter": lambda a, b, **params: a - b}
```

## Custom Formatters

If you defined a function as a custom formatter the call signature has changed:

```python
def image_formatter(row, **kws):
    return Image(source=row["image"], height=50, spacing_above="none", spacing_below="none")

self.tabulator.columns = [
    ...
    {'title': 'Image', 'field':'image', 'formatter': image_formatter},
]

# becomes

def image_formatter(cell, **kws):
    return Image(source=cell.get_value(), height=50, spacing_above="none", spacing_below="none")

# Alternatively

self.tabulator.columns = [
    ...
    {'title': 'Image', 'field':'image', 'formatter': Image, 'formatter_params': lambda cell: dict(source=cell.get_value(), height=50, spacing_above="none", spacing_below="none")},
]

```

If you previously used the `'date'` or `'datetime'` formatter, these would have worked for either date or datetime objects.
Now the cell value must be a date object if using the `'date'` formatter, likewise with datetime.

date and datetime `formatter_params` used to support an `outputFormat` like `"MM/DD/YYYY"`.
This is no longer supported. Instead the format should match what you would use for `strftime()`.
Note that the `outputFormat` param can be replaced by just `format`

e.g.
```python
    {
        "title": "Date Of Birth",
        "field": "dob",
        "editor": "date",
        "align": "center",
        "sorter": "date",
        "formatter": "date",
        "formatter_params": {"format": "%d/%m/%Y"},
    },

```

### Events

The `row_selection_change` event was renamed to `row_selection_changed`
(since that's what it's called in JS Tabulator).
If you made use of this event you should remove it from the designer view before making the switch.
Once you've made the switch you can hook up the new event name.
If you forget to do this, you can always switch back to `v1.0.0` remove it from the designer.

The call signatures for events have now changed. The parameters now match those of JS Tabulator.

e.g.

```python
def row_click(self, row, **event_args):
    print(row) # python dictionary

# becomes
def row_click(self, row, **event_args):
    print(row) # javascript tabulator row component
    print(row.get_data()) # python dictionary
```

```python
def cell_click(self, field, row, **event_args):
    if field == "name":
        ...

# becomes
def cell_click(self, cell, **event_args):
    field = cell.get_field()
    data = cell.get_data()
    if field == "name":
        ...

```

You can reset the call signatures by:
  - cutting the function from the code view
  - switching back to the design view
  - clicking the event handler in the designer view
  - pasting the function back

You can also check the possible event_args by going to Tabulator.info and finding the events


### Methods
Tabulator methods (the ones from the autocomplete) may previously have wrapped
a JS Tabulator method.
Now calling any Anvil Tabulator method directly calls the underlying javascript method.
This means keywords arguments are no longer supported and you should look through the Tabulator.info docs
for the correct call signatures

e.g. `add_sort` which previously used `ascending=True` now expects a `dir` argument to be either `"asc"` or `"desc"`
```python
self.tabulator.set_sort("name", ascending=True)
# becomes
self.tabulator.set_sort("name", "asc")
```

### Properties
Some properties were removed from the designer.
You should change a few properties in the designer after migration to force the designer spec to update.

The following properties are supported in the designer:
```python
"auto_columns": False,
"header_visible": True,
"height": "",
"index": "id",
"layout": "",
"pagination": True,
"pagination_size": 5,
"data" # set at runtime
"columns" # set at runtime
"column_defaults": # set at runtime
```

Other properties can be added via the `options` attribute.

e.g.
```python
self.tabulator.options.update({
    "selectable": "highlight",
    "pagination_size_selector": [1, 2, 5, 10]
})
# or just
self.tabulator.options = {
    "selectable": "highlight",
    "pagination_size_selector": [1, 2, 5, 10]
}
```

The reason for this change is that something like, `pagination_size_selector`, can also take a value of `True`.
This can't easily be expressed in the designer view of a property.


### row_selectable

If you made use of the `row_selectable` column with checkboxes. That feature has been removed as a propert.
You will now need to explicitly define the column in your column definition.

```python
from tabulator.Tabulator import row_selection_column

...

    self.tabulator.columns = [
        row_selection_column,
        {"title": "Name", "field": "name", ...},
        ...
    ]
    self.tabulator.options["selectable"] = "highlight"
```
