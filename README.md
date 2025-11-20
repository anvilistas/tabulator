# Anvil Tabulator

A dependency for anvil.works that wraps the JavaScript Tabulator Library (version 5.2)

This app is available as a [third party dependency](https://anvil.works/forum/t/third-party-dependencies/8712) using the code: `TGQCF3WT6FVL2EM2`

|                       |                                                                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dependency Clone Link | [<img src="https://anvil.works/img/forum/copy-app.png" height='40px'>](https://anvil.works/build#clone:TGQCF3WT6FVL2EM2=SMZUM3MICK67JEIH25IJXCWP) |
| Live Example          | [example-tabulator.anvil.app](https://example-tabulator.anvil.app/)                                                                               |
| Example Clone Link    | [<img src="https://anvil.works/img/forum/copy-app.png" height='40px'>](https://anvil.works/build#clone:JVL5ORAAPZ6SVWDU=JA27THWRHTGHH7XK4U36PRN4) |

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
- [Working with Data Sources](#working-with-data-sources)

---

### Creating a Tabulator Component

In JS Tabulator a tabulator instance is defined like:

```js
var table = new Tabulator("#example-table", {
  data: tabledata,
  columns: [
    { title: "Name", field: "name", width: 150 },
    { title: "Age", field: "age", hozAlign: "left", formatter: "progress" },
    { title: "Favourite Color", field: "col" },
    {
      title: "Date Of Birth",
      field: "dob",
      sorter: "date",
      hozAlign: "center",
    },
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

_(The only exception to this is `set_query()` which does support kwargs)_

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

You can check whether a tabulator instance has been built using the `self.tabulator.initialized` property.

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

If you need the `onRendered` callback. You can add a `cell_render` option to your column definition.
e.g.

```python

    columns = [
        ...,
        {"title": "Sparkline Column", ..., "cell_render": self.sparkline_render},
    ]

    def sparkline_render(self, cell):
        el = cell.getElement()
        jQuery(el).sparkline(cell.getValue(), {"width":"100%", "type":"bar"})

```

**Security**:

Strings returned from a custom formatter will become the innerHTML of the cell.
This allows you to use dom strings like `f"<span style={'red'}>{cell.get_value()}</span>"`,
but it can cause security issues where the value of the cell is something you do not control (see xss attacks).
If you just want to display text with a custom formatter, it may be better to return an Anvil Label with the `text` property assigned to the data.

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
When raised without a `value` paramater this is equivalent to `self.raise_event("x-cancel")`.
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


_NB: To turn off a sorter for a particular column set the `"header_sort"` to `False`._


**Custom Filters**

In JS Tabulator

```js
function customFilter(data, filterParams) {
  //data - the data for the row being filtered
  //filterParams - params object passed to the filter

  return data.name == "bob" && data.height < filterParams.height; //must return a boolean, true if it passes the filter.
}

table.setFilter(customFilter, { height: 3 });
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
import { Tabulator, FormatModule, EditModule } from "tabulator-tables";

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

**NB**
You can only register modules before the first Tabulator instance is created.
Subsequent calls to `Tabulator.register_module` will have no effect.

---

### Themes

Anvil Tabulator uses JS Tabulator's `"bootstrap3"` theme.

Some other pre-written themes can be used with Anvil Tabulator.

**Changing the theme**

```python
from tabulator.Tabulator import Tabulator

Tabulator.theme = "midnight"
# Included themes are:
# - "standard",
# - "simple",
# - "midnight",
# - "modern",
# - "bootstrap3",
# - "bootstrap4",
# - "materialize"

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

**NB**
You can only change the theme before the first Tabulator instance is created.
Subsequent calls to `Tabulator.theme` will have no effect.

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

### Working with Data Sources

Anvil Tabulator provides flexible APIs for working with different data sources. This section covers:

- Simple list data (dicts)
- Anvil App Tables with remote loading
- Model/class-based data
- Combining models with App Tables

#### Basic Data: Lists of Dictionaries

The simplest way to use Tabulator is with a list of dictionaries:

```python
self.tabulator.data = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 25},
]
self.tabulator.columns = [
    {"title": "Name", "field": "name"},
    {"title": "Age", "field": "age"},
]
```

That's it! No additional configuration required for basic usage.

---

#### Working with App Tables

Anvil Tabulator provides an API for working with Anvil `app_tables` with remote data loading, pagination, and filtering.

**Basic Setup**

**Your table should have a unique ID column.** Set Tabulator's `index` property to specify which column to use as the unique identifier:

```python
self.tabulator.options = {
    "app_table": app_tables.my_table,
    "index": "uid",  # Required: your unique ID column name
    "data_loader": False,  # Display JS Tabulator's 'loading' component
    "loading_indicator": True,  # Use Anvil spinner during page loading (default)
}
```

Tabulator expects each data object to have an `index` key to work with the data effectively. If you don't have a unique ID column, Tabulator will fall back to using the row ID.

_You may want to make a server call to retrieve a `client_readable` view of an `app_table`_

When an `app_table` option is provided, data is retrieved by calling `.search()` with sorting applied automatically based on header clicks.

**Progressive Loading and Pagination**

For large datasets, use progressive loading:

```python
# Option 1: Load mode - fetch new pages as needed
self.tabulator.options = {
    "app_table": app_tables.my_table,
    "height": 400,
    "pagination": False,
    "progressive_load": "load",
    "progressive_load_delay": 200,  # ms between requests
}

# Option 2: Scroll mode - load as user scrolls
self.tabulator.options = {
    "app_table": app_tables.my_table,
    "height": 400,
    "pagination": False,
    "progressive_load": "scroll",
    "progressive_load_scroll_margin": 300,  # px from bottom to trigger load
}
```

**Queries and Filtering**

Use `set_query()` to filter data (similar to JS Tabulator's `set_filter()` but for app_tables):

```python
import anvil.tables.query as q

def text_box_1_change(self, **event_args):
    name = self.text_box_1.text
    if not name:
        self.tabulator.clear_query()
    else:
        self.tabulator.set_query(name=q.ilike(f"%{name}%"))
```

Any valid Anvil query API syntax is supported.

**Retrieving App Table Rows**

In event handlers, use `.get_table_row()` or `.get_table_rows()` to access the original app_table rows:

```python
def tabulator_row_click(self, row, **event_args):
    # row is a tabulator row component
    # row.get_data() returns a JavaScript-wrapped data object
    data = row.get_data()

    # row.get_table_row() returns the original anvil app_table row 😃
    table_row = row.get_table_row()

def tabulator_cell_edited(self, cell, **event_args):
    table_row = cell.get_table_row()  # Also works on cells

def select_visible(self):
    # Returns a list of app_table rows that are visible
    visible_rows = self.tabulator.get_table_rows("visible")
```

**Refreshing Data**

All queries and searches are cached. To reload/refresh data:

```python
# Refresh and stay on current page
current_page = self.tabulator.get_page()
self.tabulator.replace_data()  # or self.tabulator.set_data()
self.tabulator.set_page(current_page)
```

This creates a fresh call to `search()` on the `app_table`, clearing cached values.

**Row Cache Management**

For performance, rows and data are cached when using the `app_table` option. If you update a table row or add a new row, clear the cache:

```python
self.tabulator.clear_app_table_cache()
self.tabulator.replace_data()  # Reload with fresh data
```

**Row Selection Column with App Tables**

Using the `row_selection_column` does **not** work well with the `app_table` option unless you use:

```python
self.tabulator.options = {
    "app_table": app_tables.my_table,
    "progressive_load": "load",
    "pagination": False,
}
```

---

#### Working with Models

Instead of dictionaries, you can use custom classes (models) to represent your data.

**Defining Models**

Define a model class that represents your data structure:

```python
class Author:
    def __init__(self, uid, name, birth_year):
        self.uid = uid
        self.name = name
        self.birth_year = birth_year

    @property
    def age(self):
        from datetime import datetime
        return datetime.now().year - self.birth_year
```

**Setup for Model Data**

```python
self.tabulator.columns = [
    {"title": "Name", "field": "name"},
    {"title": "Age", "field": "age"},
]
self.tabulator.options = {
    "index": "uid",  # Required: unique identifier field
    "use_model": True,
    "getter": getattr,  # Use getattr instead of dict access
}
self.tabulator.data = my_list_of_authors
```

**Why `getter: getattr`?**

By default, Tabulator uses `operator.getitem` (dictionary access: `data["field"]`). For model classes with attributes, change the getter to `getattr()` so it uses `data.field` instead.

**Retrieving Models from Events**

Use `get_model()` or `get_models()` to access the original model instances:

```python
def tabulator_row_click(self, row, **event_args):
    # row is a tabulator row component
    model = row.get_model()  # Returns the Author instance
    print(f"Clicked: {model.name}, age {model.age}")

def tabulator_cell_edited(self, cell, **event_args):
    model = cell.get_model()

def select_visible(self):
    # Returns a list of model instances that are visible
    visible_models = self.tabulator.get_models("visible")
```

---

#### Combining Models with App Tables

When using `app_table` data sources, rows may be instances of model classes rather than plain data tables rows. These models can have computed properties or methods that don't exist as columns in the underlying database.

There are two ways to work with models and app_tables:

**1. Anvil Model Classes** (Recommended for Anvil Data Tables)

If your Data Table has a [model class defined](https://anvil.works/docs/data-tables/model-classes), rows from a `client_readable` view are automatically instances of that model class:

```python
# Server-side: model class is defined for app_tables.books
@tables.model_class('books')
class Book:
    @property
    def display_name(self):
        return f"{self.title} by {self.author}"

    @property
    def is_recent(self):
        return (datetime.now() - self.published_date).days < 365

# Client-side: rows are already Book instances
books_view = anvil.server.call('get_books_view')  # Returns client_readable view

self.tabulator.options = {
    "app_table": books_view,
    "index": "isbn",
    # No mutator needed - rows are already Book instances
    # No use_model needed - only for standalone lists
}
```

**2. Custom Classes with Mutator** (For other class types)

For custom classes (like `anvil_extras.persistence` or your own classes), use the `mutator` option to transform each row:

```python
from anvil_extras.persistence import persisted_class

@persisted_class
class Book:
    key = "title"

    @property
    def display_name(self):
        return f"{self.title} by {self.author}"

self.tabulator.options = {
    "app_table": app_tables.books,
    "mutator": Book,  # Transform each row into a Book instance
    "index": "title",
    "getter": getattr,
}
```

**Sorting Considerations for Both Scenarios**

When using `app_table`, sorting normally happens on the remote database. This is efficient for large datasets because only the requested page is fetched.

However, **computed properties** (like `Book.display_name` or `Book.is_recent` above) don't exist as database columns, so remote sorting isn't possible for these fields.

**Custom Sort Keys**

Use the `custom_sort_keys` option to define client-side sort functions for computed properties:

```python
# Works with both Anvil model classes AND custom classes
self.tabulator.options = {
    "app_table": books_view,  # or app_tables.books with mutator
    "index": "isbn",
    "custom_sort_keys": {
        "display_name": lambda book: book.display_name,
        "is_recent": lambda book: book.is_recent,
        "priority": lambda book: book.calculate_priority(),
    }
}

self.tabulator.columns = [
    {"title": "ISBN", "field": "isbn", "sorter": True},  # Remote sort (DB column)
    {"title": "Title", "field": "title", "sorter": True},  # Remote sort (DB column)
    {"title": "Display", "field": "display_name", "sorter": True},  # Custom sort
    {"title": "Recent", "field": "is_recent", "sorter": True},  # Custom sort
]
```

**How Custom Sort Keys Work**

When a user sorts by a field listed in `custom_sort_keys`:

1. **All matching data** is fetched from the remote source (respecting any filters/queries)
2. The custom sort function is applied **client-side** in Python
3. Results are sorted and paginated
4. The requested page is displayed

**Important Trade-offs**

⚠️ **Performance Implications:**

- Custom sorting requires fetching **all matching rows**, not just one page
- Sorting happens in Python on the client
- Lazy loading benefits are lost when sorting by custom keys
- Performance depends on total dataset size, not page size

💡 **Best Practices:**

- Use remote sorting (database columns) whenever possible for large datasets
- Reserve `custom_sort_keys` for computed properties that can't be database columns
- Consider adding frequently-sorted computed values as actual database columns if possible
- Use `progressive_load: "load"` for better UX during the initial data fetch
- Be mindful of dataset size - works well for hundreds of rows, may struggle with thousands

**Multiple Sort Keys**

Sorts are applied in the order specified by the user:

```python
"custom_sort_keys": {
    "priority": lambda item: item.calculate_priority(),
    "status": lambda item: item.status_order(),
}
```

If sorting by `[{"field": "priority", "dir": "asc"}, {"field": "status", "dir": "desc"}]`, items are first sorted by priority (ascending), then by status (descending) for ties.

**Mixing Remote and Custom Sorts**

You can mix remote (database) and custom sorts in the same table. The UX is seamless - users don't see the difference:

```python
self.tabulator.columns = [
    {"title": "Title", "field": "title", "sorter": True},  # Remote: efficient
    {"title": "Author", "field": "author", "sorter": True},  # Remote: efficient
    {"title": "Display", "field": "display_name", "sorter": True},  # Custom: fetches all data
]
```

## Debug Logging

By default debug logging is disabled. To enable it use the following code:

```python
from tabulator.Tabulator import Tabulator
Tabulator.debug_logging(True)
```

Debug logging will show python debug messages during instantiation and initialization of the tabulator component.
This can be helpful for debugging issues with the tabulator component.

The underlying JavaScript tabulator component also has a debug logging feature.
See the tabulator docs for debug logging and add these options to the tabulator options.

Messages from the JavaScript Tabulator component will be logged to the browser console.
